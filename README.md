# T_SWE_2023_2024


# Removing submodules
https://stackoverflow.com/a/1260982
To remove a submodule, first use

```
git rm <path-to-submodule>
```

This removes the filetree and the submodule entry in .gitmodules

To remove the submodules .git directory, use

```
rm -rf .git/modules/<path-to-submodule>
git config --remove-section submodule.<path-to-submodule>
```

Then commit your changes.
