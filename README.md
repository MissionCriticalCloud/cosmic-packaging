# Packaging

## Cloning the Packaging repository

In order to clone the Packaging repository please follow the steps below:

1. Fork the repository
2. Clone the repository: 
   - git clone git@github.com:MissionCriticalCloud/packaging.git
   - Please make sure that you have a deployment key (ssh key) in your profile. See references for more details
3. Execute the following comment:
   - ./package_cosmic -d centos7 -f [path_to_cosmic]

## Dependencies

Before packging the RPMs, please make sure that you have built Cosmic. Find out how to build Cosmic here: [Cosmic](https://github.com/MissionCriticalCloud/cosmic). 

## References

* [Generating an SSH key]{https://help.github.com/articles/generating-an-ssh-key/}
