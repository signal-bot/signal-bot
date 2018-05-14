# Contributing

[Fork and clone the repository][fork]:

    git clone git@github.com:your-username/signal-bot.git

Verify that all existing tests pass by executing the test suite via [nose][nose]:

    nosetests

Run the [flake8][flake8] utility on every python file in the package to verify coding style consistency and comply with the [style guide][style].

Push a feature branch to your fork and submit a pull request.
Refer to [this guide][commits] on how to write good commit messages.

## Sign-off

By making a contribution (pull requesting or committing) to the signal-bot project you certify that

* you have the right to submit it to signal-bot.

* you created the contribution/modification; or you based it on previous work that, to the best of your knowledge, is covered by a compatible open source license; or someone who did one of the former provided you with this contribution/modification and you are submitting it without changes.

* you understand and agree that your contribution/modification to this project is public and that a record of it (including all information you submit with it, including copyright notices and your sign-off) is maintained indefinitely and may be redistributed consistent with signal-bot's AGPL v3 license or the open source license(s) involved.

To make your certification explicit we borrow the "sign-off" procedure from the Linux kernel project, i.e., each commit message should contain a line saying

    Signed-off-by: Name Sirname <name.sirname@example.org>

using your real name and email address.
Running the git-commit command with the -s option automatically adds this line.

[fork]: https://help.github.com/articles/cloning-a-repository/
[nose]: https://nose.readthedocs.org/en/latest/
[flake8]: http://flake8.pycqa.org/en/latest/
[style]: https://www.python.org/dev/peps/pep-0008/
[commits]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
