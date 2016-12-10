# farg
Implementation of ideas from the FARG group (http://www.cogsci.indiana.edu/)

The implementation here is primarily inspired by the descriptions in the book _Fluid Concepts and Creative Analogies_ by [Douglas Hofstadter](https://en.wikipedia.org/wiki/Douglas_Hofstadter).

The end goal of this process to create someting like an automatic troubleshooter to aid in debugging problems that might come up at work. 
But this is quite a ways off. I have some vague ideas about encoding notions of the types of tests to run and how those results might be applied.
But for now, I am starting with activities that have been known to be implementable to act as a baseline to create the base architecture. 

## NUMBO
At the moment the only sub-project is an implemtation of "Numbo", originally by Daniel Defays and described in a chapter in the book above. 

The task of Numbo is to solve math puzzles where you are given a target number and numbers which will be used to make up the solution.
The numbers must be combined using simple math operations (addition, subtraction, multiplication) in order to arrive at the target. 

A trivial example would be:
TARGET: 10
BRICKS: 2 3 5 12

One solution would be (5 + 3) + 2 = 10
Another one might be (12 - 2) = 10

Obviously this could be easily solved by a simple program which takes a brute force approach of trying every combination. 
However that is not the goal of any program in the "[Fargitecture](https://farg.wordpress.com/tag/fargitecture/)" style. 
Instead, Numbo "notices" that the inputs are small numbers and so likely would involve addition. 
Additionally, as Numbo is "reading" the inputs, it is "thinking about" what operations could be performed on those specific numbers 
_and numbers like them_. 

So as time moves forward, certain portions of "permanent memory" trigger the execution of "codelets" which will attempt to actually do useful work.
For example, an operation to "try to add 8 and 2" might trigger. In this case, the actual input does not include an "8", so that immediate tasks fails.
But it _might_ trigger the execution of an operation to try attempt to generate the "8" as a sub-target. In our case, 5 and 3 can be added to do that. 

Execution proceeds in that way. But the key is that there are other operations all happening in parallel at the same time along different avenues to solve the problem.
Here "parallel" is more akin to the timeslicing that occurs within an operating system. There is only ever one trivial operation
executing at a time. So the larger operations of "try to add 8 and 2" is actually broken up into:

* Attempt to find numbers similar to 8 and 2
* If found, add the numbers that do get found (which might actually instead be 7 and 1)
* After being added together, store in our workspace the fact that we now have access to the result of that operation

Each of those individual operations is known as a "codelet", and will _randomly_ run (with some weighting) from the pool of other codelets vying for attention. 

