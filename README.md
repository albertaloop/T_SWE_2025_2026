# T_SWE_2025_2026

This repository references three modules Controller, Firmware, and FSM. These modules contain all of the software for Albertaloop during the 2025-2026 school year. 

Modules:
1. Controller/ contains the GUI that runs on the controller raspberry pi (client) connected to SX1276 LORA and allows user to send the relevant commands to the rover.

2. FSM/ contains the main code that runs on the Main Processing Unit/ Raspberry pi (server) on the pod. It receives the messages sent by the controller/LORA and sends them over to the CANbus.

3. Firmwares/ contains the codes to the nucleo boards subsystems: LED controller, Motor controller, and Braking module.  

Branches info:
Branch CANdrivers contains the following drivers:
- Loopback
- Loopback IT
- Normal 2 node mode
With normal 2 node mode, the bus can be tested - sends data both ways and requests RTR

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
