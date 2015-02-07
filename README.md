Install
=======

```shell
pip install twisted-dev-tools
```

Examples
========

```shell
fetch-ticket <ticket-number>
review-tickets
get-attachment get <ticket-number> # Gets latest attachment from ticket
tch-ticket works :)
get-attachment apply <ticket-number> # Gets latest attachment from ticket, applies it to the current git reposiory, and commits it with an appropriate message.
make-branch <branch-name> # Creates an svn branch with the given name
force-build # Force-builds the current git branch, assuming it has been push'd (with dcommit) to svn
```
