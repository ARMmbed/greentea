  * [Contributing](#contributing)
    * [Enhancements vs bugs](#enhancements-vs-bugs)
    * [Workflow](#workflow)
      * [Forking and cloning this repository](#forking-and-cloning-this-repository)
      * [Issues solving](#issues-solving)
      * [Code review](#code-review)
    * [Issues and bug reporting](#issues-and-bug-reporting)
  * [How to contribute](#how-to-contribute)
    * [Testing and code coverage](#testing-and-code-coverage)
    * [Code coverage](#code-coverage)
  * [Keep your GitHub fork updated](#keep-your-github-fork-updated)
      * [Tracking changes](#tracking-changes)
      * [Verify with:](#verify-with)
      * [Updating](#updating)
  * [Final notes](#final-notes)

# Contributing
We really appreciate your contributions! We are an open source project and we need your help. We want to keep it as easy as possible to contribute changes that get things working in your environment. There are a few guidelines that we need contributors to follow so that we can have a chance of keeping on top of things.
## Enhancements vs bugs
Enhancements are:
* New features implementation.
* Code refactoring.
* Coding rules or coding style improvements.
* Code comments improvement.
* Documentation work.
Bugs are:
* Issues raised internally or externally by application users.
* Internally (from the ARM mbed team) created issues from the Continuous Integration pipeline and build servers.
* Issues detected using automation tools such as compilers, sanitizers, static code and analysis tools.

## Workflow
### Forking and cloning this repository
First [fork](https://help.github.com/articles/fork-a-repo/) this repository in GitHub, then clone it locally with:
```
$ git clone <repo-link>
```
Now you can create separate branches in the forked repository and prepare pull requests with changes.
### Issues solving
Simple workflow issue solving process may contain below steps:
1. Issue filed (by any user).
2. Proper label assigned by gate-keeper.
3. Bug-fixer forked and cloned.
4. Optional clarifications made using the Issues tab's Comment section.
5. Pull request with fix created.
6. Pull request reviewed by others.
7. All code review comments handled. 
8. Pull request accepted by gate-keeper.
9. Pull request merged successfully.

### Code review
The code review process is designed to catch both style and domain specific issues. It is also designed to follow and respect the _definition of done_. Please make sure your code follows the style of the source code you are modifying. Each pull request must be reviewed by the gate-keeper before we can merge it to the master branch.
## Issues and bug reporting
Please report all bugs using the Issues tab on the GitHub webpage. It will help us to collaborate on issues more promptly. One of our gate-keepers (developers responsible for quality and the repository) will review the issue and assign a label such as _bug_, _enhancement_, _help wanted_ or _wontfix_.
# How to contribute
You can either file a bug, help fix a bug or propose a new feature (or enhancement) and implement it yourself. If you want to contribute please:
* Bug reports: File a bug report in the Issues tab of this repo to let us know there are problems with our code.
  * Make sure your bug report contains a simple description of the problem.
  * Include information about the host computer's configuration and OS or VM used.
  * Include information about the application's version. All applications should have at least a ``--version`` switch you can use to check the version.
  * Copy/paste useful console dumps and configuration files' content. Please use [fenced code blocks](https://help.github.com/articles/github-flavored-markdown/#fenced-code-blocks) to encapsulate code snippets.
* New features or bug fix: Create a pull request with your changes. 
* General feedback: Give your feedback by posting your comments on existing pull requests and issues.

## Testing and code coverage
The application should be unit tested (at least a minimal set of unit tests should be implemented in the ``/test`` directory). We should be able to measure the unit test code coverage. 
Run a unit test suite to make sure your changes are not breaking current implementation:
```
$ cd <package>
$ python setup.py test
```
## Code coverage
To measure application code coverage for unit tests please use the coverage tool. This set of commands will locally create a code coverage report for all unit tests:.
```
$ cd <package>
$ coverage –x setup.py test
$ coverage –rm
$ coverage html
```
# Keep your GitHub fork updated
I want to fork a GitHub repo SOME_REPO/appname to USER/appname and want to keep it updated.
### Tracking changes
```
$ git clone git@github.com:USER/appname.git
$ cd appname
$ git remote add upstream git@github.com:SOME_REPO/appname.git
```
### Verify with:
```
$ git remote -v
origin  https://github.com/USER/appname.git (fetch)
origin  https://github.com/USER/appname.git (push)
upstream  https://github.com/USER/appname.git (fetch)
upstream  https://github.com/USER/appname.git (push)
```
### Updating
Each time I want to update, from my local master branch I will do the following:
```
$ git fetch upstream
$ git rebase upstream/master
```
The goal of the rebase is to have a cleaner history if I have local changes or commits on the repo.
# Final notes
1. Please do not change the version of the package in the ``setup.py`` file. The person or process responsible for releasing will do this and release the new version.
2. Keep your GitHub updated! Please make sure you are rebasing your local branch with changes so you are up to date and it is possible to automatically merge your pull request.
3. Please, if possible, squash your commits before pushing to the remote repository.
4. Please, as part of your pull request:
  * Update ``README.md`` if your changes add new functionality to the module.
  * Add unit tests to the ``/test`` directory to cover your changes or new functionality.
