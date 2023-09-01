#!/bin/bash
IFS=$(echo -en "\n")
for file in *.yaml; 
do 
    ansible-playbook -i hosts $file --vault-id @vault.py
done