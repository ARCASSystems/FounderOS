# Improving the skill

Read this when you have run the test cases and are ready to improve the skill.

This is the heart of the loop. You have run the test cases, the user has reviewed the results, and now you make the skill better.

## How to think about improvements

1. **Generalize from the feedback.** You are trying to build a skill that works across many different prompts, not just the handful you are iterating on. Avoid fiddly, overfit changes and oppressively constrictive MUSTs. If an issue is stubborn, try a different metaphor or a different pattern of working. It is cheap to try.
2. **Keep the prompt lean.** Remove things that are not pulling their weight. Read the transcripts, not just the final outputs. If the skill is making the model waste time on unproductive steps, cut the parts causing that and see what happens.
3. **Explain the why.** Explain the reasoning behind everything you ask the model to do. Modern models have good theory of mind and go beyond rote instructions when given a good harness. If you find yourself writing ALWAYS or NEVER in all caps, that is a yellow flag. Reframe and explain the reasoning instead.
4. **Look for repeated work across test cases.** If all the test runs independently wrote a similar helper script or took the same multi-step approach, that is a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it.

Take your time and mull it over. Write a draft revision, then look at it anew and improve it.

## The iteration loop

After improving the skill:

1. Apply your improvements.
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs.
3. Show the user the new results next to the previous iteration.
4. Wait for the user to review.
5. Read the new feedback, improve again, repeat.

Keep going until the user says they are happy, the feedback is all empty, or you are not making meaningful progress.
