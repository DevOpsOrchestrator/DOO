#!/bin/bash

# Loop através de todos os arquivos .yml e .yaml no diretório
for arquivo in *.yaml *.yml; do
    # Verifica se o arquivo não é oculto
    if [[ ! $arquivo == *"/."* ]]; then
        # Verifica se o arquivo é um arquivo regular (não um diretório)
        if [[ -f $arquivo ]]; then
            # Executa o arquivo
            echo executing $arquivo
            ansible-playbook -i hosts $arquivo --vault-id @vault.py
        fi
    fi
done