#!/bin/bash

DISK_FILE="/home/luka/Projet/stress/testfile"

echo "=== Test CPU, RAM et disque toutes les 25 secondes ==="

while true; do
    echo "=== Nouveau cycle ==="

    # CPU : 2 cœurs à 25% pendant 10s
    stress-ng --cpu 2 --cpu-load 25 --timeout 10s &

    # RAM : 2 threads à 30% de RAM pendant 10s
    stress-ng --vm 2 --vm-bytes 30% --vm-keep --timeout 10s &

    # Disque : fichier de 2Go
    dd if=/dev/zero of="$DISK_FILE" bs=1M count=2048 &

    # Attendre la fin des trois tâches
    wait

    # Supprime le fichier disque
    rm -f "$DISK_FILE"

    echo "Cycle terminé. Pause de 25 secondes..."
    sleep 25
done

