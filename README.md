# travis-tp

## Background
Basically, instead of running the current set TS of test suites once for a given commit, some subsets of TS are run more than once on the commit for a different combination of <Ruby version,GEM configuration> (cf. your screenshot).

This potentially leads to inefficient test execution:
- If a given test suite T1 in TS, when it fails, always fails on all combinations, then technically that test suite should only be scheduled once, for one <Ruby version,GEM configuration>, instead of for all the combinations.
- If a given test suite T1 in TS fails only for specific Ruby versions, and does that on all GEM configurations, again less executions are necessary.
- The same for if a given test suite fails for a specific GEM, across all Ruby versions.
- Perhaps there are other patterns as well?


     The idea is to first identify patterns of needless TS execution that lead to wasteful executions, such as:
    (1) a TS fails for any Ruby version for a specific GEM configuration,
    (2) a TS fails for any GEM configuration for a specific Ruby version,
    (3) a tS fails for any GEM configuration for any Ruby version,
    and (4) may be more.
    
    After identifying these cases, we may compare their execution and demonstrate the possible
    savings by avoiding the needless execution of failing TS(s).
    If I understand correctly, we are shifting our focus from energy consumption to execution time, right?

=> Yes, in the interest of time. Also, the execution time analysis would make sense both for test prioritization and selection, instead of just selection.

    About downloading the build logs you are referring to these logs[https://github.com/elbaum/CI-Datasets], right?

=> Yes, you would just need to crosslink each build with its corresponding Ruby/Gem information.

## Research Questions
So, the goal of the project could be to address the following RQs:
1. How common are the above cases of test execution redundancy?
2. Can existing test selection approaches be made <Ruby,GEM>—aware in an efficient way?
3. Can existing test prioritization approaches be made <Ruby,GEM>—aware in an efficient way?

## Datasets
Ruby on Rails could be used to do the evaluation, but just would need to check how explicit the test suite execution/success/failure data is in the build logs (which you would need to download).
