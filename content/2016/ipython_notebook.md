Title: Setting up IPython with Git
Date: 2016-01-17
Category: ipython
lang: en

Since I've been annoyed by how IPython notebooks integrate with Git, I'd like
to share a solution for this problem.

The description can be found here: [http://stackoverflow.com/a/25765194/1239545](http://stackoverflow.com/a/25765194/1239545)

What it does is:

*  it adds a hook for saving the notebook, which also saves a _pure_ version
*  it suggests that you keep both the pure version and the notebook under version control
