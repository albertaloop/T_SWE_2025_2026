# T_SWE_2025_2026

This repository references three modules GUI, Firmware, and FSM doc. These modules contain all of the software for Albertaloop during the 2025-2026 school year. 

Instructions for using submodules: https://git-scm.com/book/en/v2/Git-Tools-Submodules </br>
Documentation for git: https://git-scm.com/docs


# Update submodules
https://stackoverflow.com/a/1032653

```
git submodule update --recursive --remote 
```


# Clone repository with all submodules and files

```
git clone --recurse-submodules https://github.com/albertaloop/T_SWE_2023_2024.git
```

To pull the changes from the main branch of a submodule, the line "branch = main" must be included in the submodule entry in .gitmodules.


# Adding a new submodule

```
git submodule add <url-to-repo>
```

This adds the submodule as a new directory of the same name. An entry for the submodule will be added to .gitmodules.

Commit and push your changes using:

```
git commit -am 'Add submodule'
git push
```


# Removing submodules
https://stackoverflow.com/a/1260982
To remove a submodule, first use:

```
git rm <path-to-submodule>
```

This removes the filetree and the submodule entry in .gitmodules

To remove the submodule's .git directory, use:

```
rm -rf .git/modules/<path-to-submodule>
git config --remove-section submodule.<path-to-submodule>
```

Then commit your changes.
