#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_LINEA    256


//Se crea un struct que va a guardar todos los datos
typedef struct {
    int   numero;
    double temperatura;
    char  tendencia[8]; 
    char  fecha[32];
} Captura;

int main(void) {
    //Se abre el archivo, si es posible
    FILE *archivo = fopen("capturas.txt", "r");
    if (!archivo) {
        printf("No se pudo abrir el archivo.\n");
        return 1;
    }


    // NUEVO: arreglo dinámico con capacidad creciente
    Captura *capturas = NULL;                             // Puntero a arreglo dinamico captura
    size_t   capacidad = 0;                               // capacidad actual
    int      n = 0;                                       // cantidad de elementos usados

    //Linea es un string temporal donde se guarda cada linea del archivo a medida que se lee
    char linea[MAX_LINEA];

    //Mientras el numero sea menos que las captural maximas, y podamos leer una linea del archivo linea
    // while (n < MAX_CAPTURAS && fgets(linea, sizeof(linea), archivo)) {   // ORIGINAL
    // NUEVO: leer todo el archivo (sin límite fijo), creciendo con realloc
    while (fgets(linea, sizeof(linea), archivo)) {
        linea[strcspn(linea, "\r\n")] = '\0';
        
        //Se crean valores temporales
        int numero;
        double temp;
        char tendencia[8];
        char fecha[32];

        //Se extraen los valores del archivo
        int ok = sscanf(linea,
                        "Captura %d: %lf%*[^,], Tendencia: %7[^,], Fecha: %31[^\n]",
                        &numero, &temp, tendencia, fecha);

        //Si se leyeron los 4 valores correctamente, se guarda como un vector en el struct
        if (ok == 4) {
            // Si n llega al maximo de capacidad, hay que agrandar el arreglo
            if (n == (int)capacidad) {
                //La capacidad del arreglo crece exponencialmente
                size_t nueva_cap;
                if (capacidad == 0) {
                    nueva_cap = 16;
                } else {
                    nueva_cap = capacidad * 2;
                }
                //Realloc pide mas memoria para el arreglo, siendo temp un puntero temporal
                Captura *tmp = realloc(capturas, nueva_cap * sizeof *capturas);
                //Si realloc falla entonces sale este error
                if (!tmp) {                                     
                    perror("realloc");
                    free(capturas);
                    fclose(archivo);
                    return 1;
                }
                capturas = tmp;                                            // NUEVO
                capacidad = nueva_cap;                                     // NUEVO
            }

            //Se añade el nuevo dato en cada numero del respectivo struct
            capturas[n].numero      = numero;
            capturas[n].temperatura = temp;
            //Para string se usa strncpy
            strncpy(capturas[n].tendencia, tendencia, sizeof(capturas[n].tendencia) - 1);
            capturas[n].tendencia[sizeof(capturas[n].tendencia) - 1] = '\0';

            strncpy(capturas[n].fecha, fecha, sizeof(capturas[n].fecha) - 1);
            capturas[n].fecha[sizeof(capturas[n].fecha) - 1] = '\0';

            //Se aumenta el numero
            n++;
        }
    }

    //Cierro el archivo
    fclose(archivo);

    // Si no hay datos válidos, terminar ordenadamente
    if (n == 0) {
        printf("No se leyeron capturas válidas.\n");
        free(capturas);                                   // NUEVO
        return 0;
    }

    // Cabecera de la tabla
    printf("%-10s %-12s %-12s %-20s\n", "Numero", "Temp (C)", "Tendencia", "Fecha");
    printf("---------------------------------------------------------------\n");

    for (int i = 0; i < n; i++) {
        // %-10s  → texto alineado a la izquierda dentro de 10 espacios
        // %-12.2f → número con 2 decimales en 12 espacios
        // %-20s   → texto con campo de 20 espacios
        printf("%-10d %-12.2f %-12s %-20s\n",
            capturas[i].numero,
            capturas[i].temperatura,
            capturas[i].tendencia,
            capturas[i].fecha);
    }


    /* MAYOR Y MENOR TEMPERATURA */
    //El mas grande
    int mayor=0;
    for(int i=0; i<n; i++){
        if(capturas[i].temperatura>capturas[mayor].temperatura){
            mayor=i;
        }
    }
    //La mas pequeña
    int menor=0;
    for(int i=0; i<n; i++){
        if(capturas[i].temperatura<capturas[menor].temperatura){
            menor=i;
        }
    }

    //Imprimir Ambas
    printf("La mayor temperatura corresponde a la captura %d \n", mayor+1);
    printf("La menor temperatura corresponde a la captura %d \n", menor+1);

    printf("Captura maxima: %.2fC, Tendencia: %s, Fecha: %s\n",
        capturas[mayor].temperatura,
        capturas[mayor].tendencia,
        capturas[mayor].fecha);

    printf("Captura minima: %.2fC, Tendencia: %s, Fecha: %s\n",
        capturas[menor].temperatura,
        capturas[menor].tendencia,
        capturas[menor].fecha);
    
    /* CALCULO ESTADISTICO */
    // Media
    double media = 0;
    for(int i = 0; i < n; i++){
        media += capturas[i].temperatura;
    }
    media = media/n;
    // %.2f para imprimir con dos decimales
    printf("La media es de %.2f grados C\n", media);
    
    // Mediana
    double mediana = 0;
    if(n%2!=0){
        mediana=capturas[n/2].temperatura;
    }else{
        mediana=(capturas[n/2].temperatura+capturas[n/2-1].temperatura)/(2);
    }
    printf("La mediana es de %.2f grados C\n", mediana);
    
    // Moda
    int repe[n];
    double moda[n];
    // Algoritmo guarda las repeticiones de cada uno
    for(int i=0; i<n; i++){
        repe[i]=0;
        moda[i]=capturas[i].temperatura;
        for(int j=0; j<n; j++){
            if(capturas[j].temperatura==moda[i]){
                repe[i]++;
            }
        }
    }

    //Ubicación del mas grande
    int pos=0;
    for(int i=0; i<n; i++){
        if(repe[i]>repe[pos]){
            pos=i;
        }
    }

    int todas_iguales = 1;
    for(int i=0; i<n; i++){
        if(repe[i] != repe[pos]){
            todas_iguales = 0;
            break;
        }
    }

    if(todas_iguales==1){
        printf("No hay moda");
    }else{
        printf("La moda es de %.2f grados C, reptiendose %d veces\n", moda[pos], repe[pos]);
    }


    //Desviación estándar
    double desv=0;
    for(int i=0; i<n; i++){
        desv+=(capturas[i].temperatura-media)*(capturas[i].temperatura-media);
    }
    desv=sqrt(desv/(n-1));

    printf("La desviacion estandar es de %.2f grados C", desv);

    // liberar memoria dinámica
    free(capturas);                                       
    return 0;
}
