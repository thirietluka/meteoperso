#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/statvfs.h>
#include <libpq-fe.h>

/*
 * Variables globales qui stockent les pourcentages
 */
long ram_percent = 0;
int cpu_percent = 0;
unsigned long disk_percent = 0;

/*
 * set_ram()
 * Lit /proc/meminfo et calcule le % de RAM utilisée
 */
int set_ram()
{
    FILE *f = fopen("/proc/meminfo", "r");

    char line[256];
    long mem_total = 0;
    long mem_available = 0;

    // Lecture ligne par ligne
    while (fgets(line, sizeof(line), f))
    {
        // Cherche "MemTotal"
        if (strstr(line, "MemTotal:"))
        {
            sscanf(line, "%*s %ld", &mem_total);
        }
        // Cherche "MemAvailable"
        else if (strstr(line, "MemAvailable:"))
        {
            sscanf(line, "%*s %ld", &mem_available);
        }
    }

    fclose(f);

    // Calcul de la RAM utilisée
    ram_percent = (mem_total - mem_available) * 100 / mem_total;

    return 0;
}

/*
 * set_cpu()
 * Compte le nombre de cores et calcule une estimation du CPU utilisé
 * grâce à loadavg / nombre de cores
 */
int set_cpu() {

    FILE *f = fopen("/proc/cpuinfo", "r");

    char line[512];
    int nb_cores = 0;

    // Compte les entrées "processor"
    while (fgets(line, sizeof(line), f)) {

        if (strncmp(line, "processor", 9) == 0) {
            nb_cores++;
        }
    }

    fclose(f);

    double loadavg[1];

    // Charge sur 1 minute
    getloadavg(loadavg, 1);

    // Convertit la charge en pourcentage
    cpu_percent = (int)(100 * loadavg[0] / nb_cores);

    return 0;
}

/*
 * set_disk()
 * Utilise statvfs pour calculer le % d'espace disque utilisé
 */
int set_disk() {

    struct statvfs stat;

    statvfs("/", &stat);

    // % = (blocs utilisés / blocs totaux) * 100
    disk_percent = (stat.f_blocks - stat.f_bfree) * 100 / stat.f_blocks;

    return 0;
}

/*
 * insert_into_db()
 * Insère les valeurs dans la base PostgreSQL
 */
void insert_into_db(PGconn *conn, int cpu, long ram, unsigned long disk) 
{
    char query[256];

    // Construction d’une requête SQL simple
    snprintf(query, sizeof(query),
             "INSERT INTO meteo_table (cpu, ram, disk) VALUES (%d, %ld, %lu);",
             cpu, ram, disk);

    PGresult *res = PQexec(conn, query);

    // Libère le résultat PostgreSQL
    PQclear(res);
}

/*
 * main()
 * - se connecte à PostgreSQL
 * - boucle infinie qui lit CPU/RAM/DISK
 * - enregistre toutes les 2 secondes
 */
int main()
{
    PGconn *conn = PQconnectdb("host=192.168.0.3 user=meteo_user password=Bxn89bxn89. dbname=meteoperso_db");

    // Vérifie que la connexion est OK
    if (PQstatus(conn) != CONNECTION_OK)
    {
        fprintf(stderr, "Erreur de connexion : %s", PQerrorMessage(conn));
        PQfinish(conn);
        return 1;
    }

    // Boucle infinie
    while (1) 
    {
        set_cpu();
        set_ram();
        set_disk();

        insert_into_db(conn, cpu_percent, ram_percent, disk_percent);

        printf("[CPU: %d%%, RAM: %ld%%, DISK: %lu%%]\n",
               cpu_percent, ram_percent, disk_percent);

        sleep(2);
    }

    PQfinish(conn);
    return 0;
}
