"""Unit economics arithmetic, done by code instead of by a model.

Scripted founder runs on 8 Oct 2026 caught the model getting this math wrong
in prose: a per-box cost off by AED 3.49 when the waste changed, and a price
for a 40 percent margin rounded down to a price that gives 39.7 percent. The
unit-economics skill calls this script for the arithmetic and keeps the
judgment (what the numbers mean, what is missing) for itself.

Standard library only. Every command prints plain text, or JSON with --json.
A number the founder did not give is never filled in quietly: where a command
counts a missing input as zero, the output says so, and per-order fees that
are missing make every contribution an upper bound.

    python scripts/unit_math.py batch --batch-cost 30 --hours 1 --hourly 40 \\
        --units 12 --waste 1 --pack-size 6 --packaging 2 --price 60
    python scripts/unit_math.py price --cost 44 --margin 40
    python scripts/unit_math.py breakeven --fixed 1200 --price 60 --variable 44
    python scripts/unit_math.py cac --sales 0 --marketing 300 --customers 4
    python scripts/unit_math.py payback --cac 75 --contribution 20 --lifetime 6
    python scripts/unit_math.py runway --cash 5000 --fixed 1000 --contribution 400 --growth 10

Percents are whole numbers: --margin 40 is forty percent, --growth 1 is one percent.
"""

from __future__ import annotations

import argparse
import json
import math
import sys


def money(value: float) -> str:
    return f"{value:,.2f}"


def as_rate(percent: float) -> float:
    """Percent in, fraction out: 40 means forty percent, and 1 means one percent.

    Percent only, on purpose. Accepting 0.4 as well made 1 ambiguous, and a
    founder who meant one percent a month got one hundred percent.
    """
    return percent / 100.0


# --------------------------------------------------------------------------- #
# The calculations. Each returns a dict: numbers plus plain-language notes.    #
# --------------------------------------------------------------------------- #

def batch(batch_cost: float, units: int, waste: int | None = None, pack_size: int = 1,
          packaging: float | None = None, hours: float | None = None,
          hourly: float | None = None, fees: float | None = None,
          price: float | None = None) -> dict:
    """Cost a batch-made product per sellable unit and per box or order.

    The cash view counts only money that leaves the business. The economic
    view adds the founder's own time at the hourly value they gave, which is a
    real cost of the business but not cash unless they pay themselves.
    """
    notes: list[str] = []
    if waste is None:
        notes.append("Waste was not given, so it is counted as 0. If part of every batch cannot be sold, "
                     "give it with --waste.")
        waste = 0
    if packaging is None:
        notes.append("Packaging was not given, so it is counted as 0 per box.")
        packaging = 0.0
    sellable = units - waste
    if units <= 0 or sellable <= 0:
        return {"error": "nothing sellable: units made must be more than units wasted"}
    if pack_size <= 0:
        return {"error": "pack size must be at least 1"}
    full_boxes, leftover = divmod(sellable, pack_size)

    time_cost = None
    if hours is not None and hourly is not None:
        time_cost = hours * hourly
    elif hours is not None or hourly is not None:
        notes.append("Your time needs both hours per batch and your hourly value. "
                     "Only one was given, so the economic view is left out.")

    def per_box(total_batch: float) -> dict:
        unit_cost = total_batch / sellable
        carry_over = unit_cost * pack_size + packaging
        out = {"cost_per_unit": unit_cost,
               "cost_per_box_leftovers_carry_over": carry_over}
        if full_boxes:
            out["cost_per_box_leftovers_wasted"] = total_batch / full_boxes + packaging
        else:
            out["cost_per_box_leftovers_wasted"] = None
        return out

    result: dict = {
        "sellable_units": sellable,
        "full_boxes": full_boxes,
        "leftover_units": leftover,
        "cash": per_box(batch_cost),
    }
    if time_cost is not None:
        result["economic"] = per_box(batch_cost + time_cost)
        result["economic"]["owner_time_per_batch"] = time_cost
        notes.append("The economic view counts your time as a cost. It is not cash "
                     "unless you pay yourself a wage.")
    if full_boxes == 0:
        notes.append(f"One batch makes {sellable} sellable units, not enough for one "
                     f"box of {pack_size}.")
    elif leftover:
        notes.append(f"{leftover} units are left after {full_boxes} full "
                     f"{'box' if full_boxes == 1 else 'boxes'}. If they "
                     f"carry over into the next batch, use the carry-over cost. If they "
                     f"are thrown away or eaten, use the wasted cost.")

    if fees is None:
        notes.append("Per-order fees (delivery, platform, payment) are unknown, so any "
                     "contribution below is an upper bound, not the real figure.")
    result["fees_per_box"] = fees

    if price is not None:
        fee = fees or 0.0
        views = {"cash": result["cash"]}
        if "economic" in result:
            views["economic"] = result["economic"]
        contribution: dict = {}
        for name, view in views.items():
            for basis in ("leftovers_carry_over", "leftovers_wasted"):
                cost = view[f"cost_per_box_{basis}"]
                if cost is None:
                    continue
                c = price - cost - fee
                contribution[f"{name}_{basis}"] = {
                    "contribution_per_box": c,
                    "margin_percent": c / price * 100 if price else None,
                }
        result["price"] = price
        result["contribution"] = contribution
    result["notes"] = notes
    return result


def price_for_margin(cost: float, margin: float, step: float = 1.0) -> dict:
    """The price that reaches a target margin, rounded UP so the margin holds."""
    if cost <= 0:
        return {"error": "cost per unit must be above zero to price for a margin"}
    if not 0 <= margin < 100:
        return {"error": "margin is a percent from 0 up to, but not including, 100"}
    rate = as_rate(margin)
    exact = cost / (1 - rate)
    rounded = math.ceil(round(exact / step, 9)) * step if step > 0 else exact
    achieved = (rounded - cost) / rounded * 100 if rounded else None
    return {"cost": cost, "target_margin_percent": rate * 100, "exact_price": exact,
            "rounded_price": rounded, "margin_at_rounded_price_percent": achieved,
            "notes": ["Rounded up, so the margin is at least the target. This is the price "
                      "the costs need, not the price the market will pay: that needs "
                      "evidence from buyers."]}


def breakeven(fixed: float, contribution: float) -> dict:
    """Units to cover fixed costs, with the zero and negative cases said plainly."""
    out: dict = {"fixed_costs": fixed, "contribution_per_unit": contribution}
    if contribution > 0:
        out["breakeven_units"] = math.ceil(round(fixed / contribution, 9)) if fixed > 0 else 0
        out["notes"] = []
    elif contribution == 0:
        out["breakeven_units"] = None
        if fixed > 0:
            out["notes"] = ["Each sale adds nothing toward the fixed costs, so they are never "
                            "recovered at any volume. Selling more does not lose more, it "
                            "just never closes the gap."]
        else:
            out["notes"] = ["With no fixed costs and no contribution, profit is zero at any "
                            "volume. There is nothing to break even on and nothing to gain."]
    else:
        out["breakeven_units"] = None
        out["notes"] = [f"Each sale loses {money(-contribution)} before fixed costs, so every "
                        f"extra sale makes the loss bigger. There is no break-even."]
    return out


def cac(sales: float | None, marketing: float | None, customers: int) -> dict:
    notes: list[str] = []
    for name, value in (("Sales spend", sales), ("Marketing spend", marketing)):
        if value is None:
            notes.append(f"{name} was not given, so it is counted as 0.")
    sales, marketing = sales or 0.0, marketing or 0.0
    spend = sales + marketing
    out: dict = {"sales_spend": sales, "marketing_spend": marketing,
                 "customers_won": customers, "spend": spend}
    if customers <= 0:
        out["cac"] = None
        notes.append("No customers were won in the period, so CAC is undefined, not zero.")
    else:
        out["cac"] = spend / customers
        if spend == 0:
            notes.append("Zero spend is rarely zero effort: say how these customers were won, "
                         "and count your time separately if it matters.")
    out["notes"] = notes
    return out


def payback(cac_value: float, contribution: float, lifetime: float | None = None) -> dict:
    """CAC payback on monthly contribution per customer, plus LTV when a lifetime is given."""
    out: dict = {"cac": cac_value, "monthly_contribution_per_customer": contribution}
    notes: list[str] = []
    if cac_value == 0:
        out["payback_months"] = 0.0
        notes.append("Acquisition cost is zero, so there is nothing to pay back. That is a "
                     "separate case from a cost that is never recovered.")
        if contribution < 0:
            notes.append(f"Each customer still loses {money(-contribution)} a month, so more "
                         f"customers make the loss bigger.")
        elif contribution == 0:
            notes.append("Each customer also adds nothing a month.")
    elif contribution <= 0:
        out["payback_months"] = None
        notes.append("Monthly contribution is zero or negative, so a positive acquisition "
                     "cost is never paid back.")
    else:
        out["payback_months"] = cac_value / contribution
    if lifetime is not None:
        ltv = contribution * lifetime
        out["ltv_contribution"] = ltv
        out["ltv_to_cac"] = ltv / cac_value if cac_value > 0 else None
        if lifetime and out.get("payback_months") and out["payback_months"] > lifetime:
            notes.append("Payback takes longer than the average customer stays.")
    out["notes"] = notes
    return out


def runway(cash: float, fixed: float, contribution: float, growth: float | None = None,
           months: int = 24) -> dict:
    """Month by month: does contribution cover fixed costs before the cash runs out?

    Contribution changes by `growth` percent each month (negative for a decline)
    and fixed costs stay flat. Default alive means the cash never runs out within
    the planning horizon AND contribution covers fixed costs at its end. A
    venture that covers its costs today but is shrinking towards a cash-out is
    not default alive.
    """
    notes: list[str] = []
    if growth is None:
        notes.append("Growth was not given, so contribution is held flat.")
        growth = 0.0
    rate = as_rate(growth)
    balance = cash
    current = contribution
    cash_out_month = None
    trail = []
    for month in range(1, months + 1):
        balance += current - fixed
        trail.append({"month": month, "contribution": current, "cash": balance})
        if balance < 0:
            cash_out_month = month
            break
        current *= (1 + rate)
    alive = cash_out_month is None and trail[-1]["contribution"] >= fixed
    covered_month = None
    if alive:
        covered_month = trail[-1]["month"]
        for row in reversed(trail):
            if row["contribution"] < fixed:
                break
            covered_month = row["month"]
    if alive:
        notes.append("Default alive at these inputs: the cash lasts the horizon and contribution "
                     "covers fixed costs at its end.")
    elif cash_out_month is not None:
        notes.append(f"Default dead at these inputs: cash runs out in month {cash_out_month}.")
    else:
        notes.append(f"Undecided within {months} months: the cash lasts, but contribution does not "
                     f"cover fixed costs by the end.")
    notes.append("Fixed costs are held flat. If a cost will rise, add it by hand. These are the inputs "
                 "you gave: try the growth you have actually seen, not the one you hope for.")
    return {"cash": cash, "monthly_fixed": fixed, "monthly_contribution": contribution,
            "monthly_growth_percent": growth, "horizon_months": months,
            "default_alive": alive, "cash_runs_out_month": cash_out_month,
            "contribution_covers_fixed_month": covered_month, "months": trail,
            "notes": notes}


# --------------------------------------------------------------------------- #
# Plain-text rendering.                                                       #
# --------------------------------------------------------------------------- #

def render(command: str, result: dict, currency: str) -> str:
    if "error" in result:
        return f"Cannot calculate: {result['error']}."
    c = f"{currency} " if currency else ""
    lines: list[str] = []
    if command == "batch":
        lines.append(f"Sellable units per batch: {result['sellable_units']} "
                     f"({result['full_boxes']} full {'box' if result['full_boxes'] == 1 else 'boxes'}, "
                     f"{result['leftover_units']} left over)")
        for view in ("cash", "economic"):
            if view not in result:
                continue
            v = result[view]
            label = "Cash cost" if view == "cash" else "Economic cost (includes your time)"
            lines.append(f"{label} per unit: {c}{money(v['cost_per_unit'])}")
            lines.append(f"{label} per box, leftovers carry over: "
                         f"{c}{money(v['cost_per_box_leftovers_carry_over'])}")
            wasted = v["cost_per_box_leftovers_wasted"]
            if wasted is not None:
                lines.append(f"{label} per box, leftovers wasted: {c}{money(wasted)}")
        if result.get("fees_per_box") is not None:
            lines.append(f"Fees per box: {c}{money(result['fees_per_box'])}")
        for key, val in result.get("contribution", {}).items():
            margin = val["margin_percent"]
            lines.append(f"Contribution per box at {c}{money(result['price'])} "
                         f"({key.replace('_', ' ')}): {c}{money(val['contribution_per_box'])}"
                         + (f", {margin:.1f}% margin" if margin is not None else ""))
    elif command == "price":
        lines.append(f"Exact price for {result['target_margin_percent']:.1f}% margin on "
                     f"{c}{money(result['cost'])}: {c}{money(result['exact_price'])}")
        achieved = result["margin_at_rounded_price_percent"]
        lines.append(f"Rounded up: {c}{money(result['rounded_price'])}"
                     + (f", which gives {achieved:.1f}%" if achieved is not None else ""))
    elif command == "breakeven":
        units = result["breakeven_units"]
        lines.append("Break-even units: " + (str(units) if units is not None else "none"))
    elif command == "cac":
        lines.append("CAC: " + (f"{c}{money(result['cac'])}" if result["cac"] is not None
                                else "undefined"))
    elif command == "payback":
        months = result["payback_months"]
        lines.append("CAC payback: " + (f"{months:.1f} months" if months is not None else "never"))
        if "ltv_contribution" in result:
            lines.append(f"LTV (contribution): {c}{money(result['ltv_contribution'])}")
            if result["ltv_to_cac"] is not None:
                lines.append(f"LTV:CAC: {result['ltv_to_cac']:.1f} to 1")
    elif command == "runway":
        lines.append(f"Default alive: {'yes' if result['default_alive'] else 'no'}")
        if result["cash_runs_out_month"] is not None:
            lines.append(f"Cash runs out in month {result['cash_runs_out_month']}")
        if result["contribution_covers_fixed_month"] is not None:
            lines.append(f"Contribution covers fixed costs from month "
                         f"{result['contribution_covers_fixed_month']}")
    lines.extend(f"Note: {n}" for n in result.get("notes", []))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Unit economics arithmetic.")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--currency", default="", help="label for money, e.g. AED")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("batch", help="cost a batch-made product per unit and per box")
    b.add_argument("--batch-cost", type=float, required=True, help="cash spent on one batch")
    b.add_argument("--units", type=int, required=True, help="units made per batch")
    b.add_argument("--waste", type=int, help="units per batch that cannot be sold")
    b.add_argument("--pack-size", type=int, default=1, help="units per box or order")
    b.add_argument("--packaging", type=float, help="packaging per box")
    b.add_argument("--hours", type=float, help="your hours per batch")
    b.add_argument("--hourly", type=float, help="what an hour of your time is worth")
    b.add_argument("--fees", type=float, help="delivery, platform and payment fees per box")
    b.add_argument("--price", type=float, help="price per box")

    p = sub.add_parser("price", help="price for a target margin, rounded up")
    p.add_argument("--cost", type=float, required=True)
    p.add_argument("--margin", type=float, required=True, help="target margin in percent, 40 for 40 percent")
    p.add_argument("--round", dest="step", type=float, default=1.0, help="round up to this step")

    e = sub.add_parser("breakeven", help="units to cover fixed costs")
    e.add_argument("--fixed", type=float, required=True)
    e.add_argument("--contribution", type=float, help="contribution per unit")
    e.add_argument("--price", type=float)
    e.add_argument("--variable", type=float, help="variable cost per unit")

    a = sub.add_parser("cac", help="customer acquisition cost")
    a.add_argument("--sales", type=float, help="sales spend in the period")
    a.add_argument("--marketing", type=float, help="marketing spend in the period")
    a.add_argument("--customers", type=int, required=True)

    y = sub.add_parser("payback", help="CAC payback and contribution LTV")
    y.add_argument("--cac", type=float, required=True)
    y.add_argument("--contribution", type=float, required=True,
                   help="monthly contribution per customer")
    y.add_argument("--lifetime", type=float, help="average customer lifetime in months")

    r = sub.add_parser("runway", help="the default alive test")
    r.add_argument("--cash", type=float, required=True)
    r.add_argument("--fixed", type=float, required=True, help="monthly fixed costs")
    r.add_argument("--contribution", type=float, required=True, help="monthly contribution now")
    r.add_argument("--growth", type=float, help="monthly growth of contribution in percent, 10 for 10 percent, "
                                                 "-5 for a 5 percent decline")
    r.add_argument("--months", type=int, default=24, help="planning horizon")

    args = parser.parse_args(argv)
    if args.command == "batch":
        result = batch(args.batch_cost, args.units, args.waste, args.pack_size, args.packaging,
                       args.hours, args.hourly, args.fees, args.price)
    elif args.command == "price":
        result = price_for_margin(args.cost, args.margin, args.step)
    elif args.command == "breakeven":
        if args.contribution is not None:
            contribution = args.contribution
        elif args.price is not None and args.variable is not None:
            contribution = args.price - args.variable
        else:
            print("Cannot calculate: give --contribution, or both --price and --variable.")
            return 2
        result = breakeven(args.fixed, contribution)
    elif args.command == "cac":
        result = cac(args.sales, args.marketing, args.customers)
    elif args.command == "payback":
        result = payback(args.cac, args.contribution, args.lifetime)
    else:
        result = runway(args.cash, args.fixed, args.contribution, args.growth, args.months)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(args.command, result, args.currency))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())
