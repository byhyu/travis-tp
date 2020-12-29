# travis-tp

## Background
Basically, instead of running the current set TS of test suites once for a given commit, some subsets of TS are run more than once on the commit for a different combination of <Ruby version,GEM configuration> (cf. your screenshot).

This potentially leads to inefficient test execution:
- If a given test suite T1 in TS, when it fails, always fails on all combinations, then technically that test suite should only be scheduled once, for one <Ruby version,GEM configuration>, instead of for all the combinations.
- If a given test suite T1 in TS fails only for specific Ruby versions, and does that on all GEM configurations, again less executions are necessary.
- The same for if a given test suite fails for a specific GEM, across all Ruby versions.
- Perhaps there are other patterns as well?


 
```
The idea is to first identify patterns of needless TS execution that lead to wasteful executions, such as:
(1) a TS fails for any Ruby version for a specific GEM configuration,
(2) a TS fails for any GEM configuration for a specific Ruby version,
(3) a tS fails for any GEM configuration for any Ruby version,
and (4) may be more.

After identifying these cases, we may compare their execution and demonstrate the possible
savings by avoiding the needless execution of failing TS(s).
If I understand correctly, we are shifting our focus from energy consumption to execution time, right?
```
    
=> Yes, in the interest of time. Also, the execution time analysis would make sense both for test prioritization and selection, instead of just selection.

    About downloading the build logs you are referring to these [logs](https://github.com/elbaum/CI-Datasets), right?

=> Yes, you would just need to crosslink each build with its corresponding Ruby/Gem information.


## Research Questions
So, the goal of the project could be to address the following RQs:
1. How common are the above cases of test execution redundancy?
2. Can existing test selection approaches be made <Ruby,GEM>—aware in an efficient way?
3. Can existing test prioritization approaches be made <Ruby,GEM>—aware in an efficient way?

## Datasets
Ruby on Rails could be used to do the evaluation, but just would need to *check how explicit the test suite execution/success/failure data is in the build logs *(which you would need to download).


    used the data from https://github.com/elbaum/CI-Datasets and added the config data (ruby version, GEM) crawled from api.travis-ci.org. we retrieved a sample as large as 100000 test suites.

## Analysis
#### RQ1: How common are the above cases of test execution redundancy?
 (1) a TS fails for any Ruby version for a specific GEM configuration      
> group by <test_suite, GEM>, if the build status are all failed, then mark it unnecessary, get 265/1516
 
 (2) a TS fails for any GEM configuration for a specific Ruby version   
> group by <test_suite, version>, if the build status are all failed, then mark it unnecessary, get 2016/4194
 
 (3) a tS fails for any GEM configuration for any Ruby version   
 > group by <test_suite>, if the build status are all failed, then mark it unnecessary, get 99/872

#### RQ2: Can existing test selection approaches be made <Ruby,GEM>—aware in an efficient way?

#### RQ3: Can existing test prioritization approaches be made <Ruby,GEM>—aware in an efficient way?


##  Contributing
## Set up environment
### Option 1: use `conda`
From the root of the repository, create a Conda environment:
 ```bash
   conda env create --file environment.yml
```
### use conda env in `jupyter notebook`
```
conda install -c anaconda ipykernel
python -m ipykernel install --user --name=travis-project
```
### Option 2: use `venv` + `pip`
TODO

## Future Work
(1) Full Dataset, currently 100,000 test suites   
(2) Focused on commit level first, then on detailed <Gem, Ruby> level   
(3)


## Reference
[1] FSE204 paper (Elbaum et al.) 2014 using Google datasets only, focused on test suite selection and prioritization (failure window + idle window + new).   
[2] 2018 using both Google datasets and rails, focused on commits prioritization.

=======
In the implementation of the additional method the following details were considered:
1. Whenever there is a tie between multiple test cases with
the same additional coverage, the test case with `less execution time` is chosen.



