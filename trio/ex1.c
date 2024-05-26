#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include "spend_time.h"

//tipo de dado para implementar a logica do trio
struct trio_t{
    int tipos_de_thread[3];
    int threads_no_trio;
    pthread_mutex_t mutex;
    pthread_cond_t cond[3];
    pthread_cond_t wait;
};

//trio vai ser uma variavel global
struct trio_t trio;

void init_trio(struct trio_t* t){
    
    //loop para iniciar cada condicao e cada posicao do vetor
    for (int i = 0; i < 3; i++) {
    	t->tipos_de_thread[i] = 0;
        pthread_cond_init(&t->cond[i], NULL);
    }
    
    //inicializacao das demais variaveis
    t->threads_no_trio = 0;
    pthread_cond_init(&t->wait, NULL);
    pthread_mutex_init(&t->mutex, NULL);
}

void trio_enter(struct trio_t* t, int my_type){

    //trava a mutex
    pthread_mutex_lock(&t->mutex);
    
    // se este tipo já está no trio, espera ate que o trio termine de executar
    while (t->tipos_de_thread[my_type-1] > 0) {
        pthread_cond_wait(&t->cond[my_type-1], &t->mutex);
    }

    // incrementa o tipo da thread e total de threads no trio
    t->tipos_de_thread[my_type-1]++;
    t->threads_no_trio++;

    // se ainda não há um trio completo, espera até que haja
    while (t->tipos_de_thread[0] == 0 || t->tipos_de_thread[1] == 0 || t->tipos_de_thread[2] == 0){
        pthread_cond_wait(&t->wait, &t->mutex);
    }

    // se este é o último a entrar no trio, acorda as threads que estao esperando o trio estar completo 
    if (t->tipos_de_thread[0] > 0 && t->tipos_de_thread[1] > 0 && t->tipos_de_thread[2] > 0) {
        pthread_cond_broadcast(&t->wait);
    }

    //destrava a mutex
    pthread_mutex_unlock(&t->mutex);
}

void trio_leave(struct trio_t* t,int my_type){

    //trava a mutex
    pthread_mutex_lock(&t->mutex);

    // decrementa o tipo no trio
    t->threads_no_trio--;

    // se este tipo for o último a sair, acorda todas as threads esperando para entrar
    if (t->threads_no_trio == 0) {
        for (int i = 0; i < 3; i++) {
    		t->tipos_de_thread[i] = 0;
    	}
        pthread_cond_broadcast(&t->cond[0]);
        pthread_cond_broadcast(&t->cond[1]);
        pthread_cond_broadcast(&t->cond[2]);
    }

    //destrava a mutex
    pthread_mutex_unlock(&t->mutex);
}

//struct para guardar os parametros de execucao de uma thread
struct thread_params{
    int t_id;
    int t_type;
    int t_solo;
    int t_trio;
};
 
void* iniciar_thread(void* arg) {

    //conversao de arg para a struct de parametros
    struct thread_params* params = (struct thread_params*) arg;
    
    // No início da thread, ela deve preencher tid, ttype, tsolo e ttrio
    //a partir dos parâmetros fornecidos na chamada pthread_create.
    int tid = params->t_id;
    int ttype = params->t_type;
    int tsolo = params->t_solo;
    int ttrio = params->t_trio;
  
    //execucao das tarefas da thread
    spend_time(tid,ttype,"S",tsolo);
    trio_enter(&trio,ttype);
    spend_time(tid,ttype,"T",ttrio);
    trio_leave(&trio,ttype);
    pthread_exit(NULL);
}

int main() {

    //iniciar a variavel trio
    init_trio(&trio);
    
    //declaracao das variaveis a serem utilizadas durante a execucao
    pthread_t *threads = NULL;
    struct thread_params *params = NULL;
    int num_threads = 0;
    int id, tipo, tempo_solo, tempo_trio;

    // loop para ler os parâmetros das threads até EOF
    while (scanf("%d %d %d %d", &id, &tipo, &tempo_solo, &tempo_trio) != EOF) {
        // cria a struct de parametros da thread
        struct thread_params param;
        param.t_id = id;
        param.t_type = tipo;
        param.t_solo = tempo_solo;
        param.t_trio = tempo_trio;

        // armazena a struct de parametros no vetor
        params = (struct thread_params*) realloc(params, (num_threads + 1) * sizeof(struct thread_params));
        params[num_threads] = param;

        // incrementa o numero de threads
        num_threads++;
    }

    // aloca espaço para as threads
    threads = (pthread_t*) malloc(num_threads * sizeof(pthread_t));

    // cria as threads com os parametros lidos
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&threads[i], NULL, iniciar_thread, &params[i]);
    }

    // espera pela finalização das threads
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // libera a memoria alocada
    free(threads);
    free(params);

    return 0;
}
