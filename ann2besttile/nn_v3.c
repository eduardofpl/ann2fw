//
// Multilayer Perceptron with Backpropagation
//
//
// Eduardo Favero Pacheco da Luz, Dr.
// 16-abr-2013
//
// Arquivo de configuracao da rede neural:
// config.ann
//

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <fcntl.h>
#include "ran3.c"

// Ponteiro para arquivo
FILE *CONFIG = NULL;
FILE *ENTRADA = NULL;
FILE *OBJETIVO = NULL;
FILE *SAIDA = NULL;
FILE *PESOS = NULL;
FILE *CURVAERRO = NULL;
FILE *FULLERRO = NULL;

// Prototipo da funcao de geracao de numeros aleatorios
float ran3(long *idum);

// Funcao para leitura de variaveis inteiras e reais
int leConfigInt(FILE *config)
{
  int value;
  char nameConfig [10];
  fscanf(config, "%s", nameConfig);
  fscanf(config, "%d", &value);
  printf("%s: %d\n",nameConfig,value);
  return(value);
};
float leConfigFloat(FILE *config)
{
  float value;
  char nameConfig [10];
  fscanf(config, "%s", nameConfig);
  fscanf(config, "%f", &value);
  printf("%s: %f\n",nameConfig,value);
  return(value);
};

// Funcao principal
int main(void)
{
  // Variaveis de configuracao da rede
  char nameConfig [10];
  float valueConfig;
  int Training, NumPattern, NumInput, NumHidden, NumOutput;

  // Avisa sobre o treinamento da rede
  printf("\nLendo arquivo de configuracao.\n");

  // Arquivo de configuracoes
  CONFIG = fopen("config.ann","r");
  if (CONFIG == NULL)
  {
    printf("Falha ao abrir arquivo de configuracao.");
    return(1);
  }

  // Le as configuracoes
  Training = leConfigInt(CONFIG);
  NumPattern = leConfigInt(CONFIG);
  NumInput = leConfigInt(CONFIG);
  NumHidden = leConfigInt(CONFIG);
  NumOutput = leConfigInt(CONFIG);

////////////////////////////////////////////////////////////////////////
// Treinando uma rede
////////////////////////////////////////////////////////////////////////
  if (Training == 1)
  {
    // Avisa sobre o treinamento da rede
    printf("\nTreinando a rede!!!\n");

    // Arquivo de dados
    ENTRADA = fopen("trainInput1par.dat","r");
    if (ENTRADA == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao abrir arquivo de entrada.\n\n");
      return(1);
    }
    OBJETIVO = fopen("trainOutputClass.dat","r");
    if (OBJETIVO == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao abrir arquivo de objetivos.\n\n");
      return(1);
    }
    SAIDA = fopen("saidaTreina.dat","w+");
    if (SAIDA == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao criar arquivo de saida.\n\n");
      return(1);
    }
    PESOS = fopen("pesos.dat","w+");
    if (PESOS == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao criar arquivo de pesos.\n\n");
      return(1);
    }
    CURVAERRO = fopen("curvaErro.dat","w+");
    if (CURVAERRO == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao criar arquivo de curva de erro.\n\n");
      return(1);
    }
    FULLERRO = fopen("fullErro.dat","w+");
    if (FULLERRO == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao criar arquivo de erro completo.\n\n");
      return(1);
    }

    // Variaveis em uso
    int    *ranpat;
    int    i, j, k, p, np, op, epoca;
    long   seed, *idum;
    float  Temp;
    double *DeltaO, *SumDOW, *DeltaH;
    double **Input, **Target, **SumH, **Hidden, **SumO, **Output;
    double **WeightIH, **WeightHO, **DeltaWeightIH, **DeltaWeightHO;
    double Erro, Ece, Esse, Omega;
    int    MaxEpoca;
    double eta, alpha, smallwt, ErroStop;

    // Lendo as variaveis de treinamento da rede
    MaxEpoca = leConfigInt(CONFIG);
    eta = leConfigFloat(CONFIG);
    alpha = leConfigFloat(CONFIG);
    smallwt = leConfigFloat(CONFIG);
    ErroStop = leConfigFloat(CONFIG);
    seed = leConfigInt(CONFIG);

    // Declaracao variaveis dinamicas
    ranpat = malloc(NumPattern*sizeof(int));
    DeltaO = malloc(NumOutput*sizeof(double));
    SumDOW = malloc(NumHidden*sizeof(double));
    DeltaH = malloc(NumHidden*sizeof(double));
    Input = malloc(NumPattern*sizeof(double));
    Target = malloc(NumPattern*sizeof(double));
    SumH = malloc(NumPattern*sizeof(double));
    Hidden = malloc(NumPattern*sizeof(double));
    SumO = malloc(NumPattern*sizeof(double));
    Output = malloc(NumPattern*sizeof(double));
    for (i = 0; i < NumPattern; i++)
    {
        Input[i] = malloc(NumInput*sizeof(double));
        Target[i] = malloc(NumOutput*sizeof(double));
        SumH[i] = malloc(NumHidden*sizeof(double));
        Hidden[i] = malloc(NumHidden*sizeof(double));
        SumO[i] = malloc(NumOutput*sizeof(double));
        Output[i] = malloc(NumOutput*sizeof(double));
    }
    WeightIH = malloc(NumInput*sizeof(double));
    DeltaWeightIH = malloc(NumInput*sizeof(double));
    for (i = 0; i < NumInput; i++)
    {
        WeightIH[i] = malloc(NumHidden*sizeof(double));
        DeltaWeightIH[i] = malloc(NumHidden*sizeof(double));
    }
    WeightHO = malloc(NumHidden*sizeof(double));
    DeltaWeightHO = malloc(NumHidden*sizeof(double));
    for (i = 0; i < NumHidden; i++)
    {
        WeightHO[i] = malloc(NumOutput*sizeof(double));
        DeltaWeightHO[i] = malloc(NumOutput*sizeof(double));
    }

    // Le os dados dos arquivos
    for (i = 0; i < NumPattern; i++)
    {
      for (j = 0; j < NumInput; j++)
      {
        fscanf(ENTRADA, "%f", &Temp);
        Input[i][j] = (double)Temp;
      }
      for (j = 0; j < NumOutput; j++)
      {
        fscanf(OBJETIVO, "%f", &Temp);
        Target[i][j] = (double)Temp;
      }
    }

    // Semente geradora de numeros aleatorios
    idum = &seed;

    // Inicializa WeightIH e DeltaWeightIH
    for(j = 0; j < NumHidden; j++)
    {
      for(i =0; i < NumInput; i++)
      {
        DeltaWeightIH[i][j] = 0.0;
        WeightIH[i][j] = 2.0 * ( ran3(idum) - 0.5 ) * smallwt;
      }
    }

    // Inicializa WeightHO e DeltaWeightHO
    for(k = 0; k < NumOutput; k ++)
    {
      for(j = 0; j < NumHidden; j++)
      {
        DeltaWeightHO[j][k] = 0.0;
        WeightHO[j][k] = 2.0 * ( ran3(idum) - 0.5 ) * smallwt;
      }
    }

    // Laco de repeticao para atualizacao dos pesos
    for(epoca = 0; epoca < MaxEpoca; epoca++)
    {

      // Ordenacao e apresentacao aleatoria de individuos
      for(p = 0; p < NumPattern; p++)
      {
        ranpat[p] = p;
      }
      for(p = 0; p < NumPattern; p++)
      {
        np = p + ran3(idum) * ( NumPattern - p );
        op = ranpat[p];
        ranpat[p] = ranpat[np];
        ranpat[np] = op;
      }

      // Inicializa as variaveis de erro
      Erro = 0.0;
      Ece = 0.0;
      Esse = 0.0;
      Omega = 0.0;

      // Laco de repeticao para todos os padroes de treinamento repeat for all the training patterns */
      for(np = 0; np < NumPattern; np++)
      {
        p = ranpat[np];
        // Calcula a ativacao das unidades escondidas
        for(j = 0; j < NumHidden; j++)
        {
          SumH[p][j] = WeightIH[0][j];
          for(i = 0; i < NumInput; i++)
          {
            SumH[p][j] += Input[p][i] * WeightIH[i][j];
          }
          Hidden[p][j] = 1.0/(1.0 + exp(-SumH[p][j]));
        }

        // Calcula a ativacao das unidades de saida e erros
        for(k = 0; k < NumOutput; k++)
        {
          SumO[p][k] = WeightHO[0][k];
          for(j = 0; j < NumHidden; j++)
          {
            SumO[p][k] += Hidden[p][j] * WeightHO[j][k];
          }
          // Saida Sigmoidal
          Output[p][k] = 1.0/(1.0 + exp(-SumO[p][k]));
          // Saida Linear
  //      Output[p][k] = SumO[p][k];
          // Calcula os erros
          // Soma dos Erros Quadraticos (SSE)
          Esse += 0.5 * (Target[p][k] - Output[p][k]) * (Target[p][k] - Output[p][k]);
          // Erro de Entropia-Cruzada (Cross-Entropy Error)
  //      Ecc -= ( Target[p][k] * log( Output[p][k] ) + ( 1.0 - Target[p][k] ) * log( 1.0 - Output[p][k] ) );
          // Saida Sigmoidal, SSE
          DeltaO[k] = (Target[p][k] - Output[p][k]) * Output[p][k] * (1.0 - Output[p][k]);
          // Saida Sigmoidal, Erro de Entropia-Cruzada
  //      DeltaO[k] = Target[p][k] - Output[p][k];
          // Saida Lineatreinamentor, SSE
  //      DeltaO[k] = Target[p][k] - Output[p][k];
        }

        //Nao faz a ultima das ultimas atualizacoes
        if ((epoca == MaxEpoca-1) && (np == NumPattern-1))
        {
          fprintf(stdout,"\n\nFim do treinamento.");
          break;
        }

        // Erro quadradico medio
        Erro = Esse;

        // Atualiza para tras os erros na camada escondida ('Back-propagate' errors to hidden layer)
        for(j = 0; j < NumHidden; j++)
        {
          SumDOW[j] = 0.0;
          for(k = 0; k < NumOutput; k++)
          {
            SumDOW[j] += WeightHO[j][k] * DeltaO[k];
          }
          DeltaH[j] = SumDOW[j] * Hidden[p][j] * (1.0 - Hidden[p][j]);
        }

        // Atualiza os pesos em WeightIH
        for(j = 0; j < NumHidden; j++)
        {
          DeltaWeightIH[0][j] = eta * DeltaH[j] + alpha * DeltaWeightIH[0][j];
          WeightIH[0][j] += DeltaWeightIH[0][j];
          for(i = 0; i < NumInput; i++)
          {
            // Ajuste do peso
//          DeltaWeightIH[i][j] = eta * Input[p][i] * DeltaH[j] + alpha * DeltaWeightIH[i][j];
            DeltaWeightIH[i][j] = eta * Input[p][i] * DeltaH[j];
            WeightIH[i][j] += DeltaWeightIH[i][j];
          }
        }

        // Atualiza os pesos em WeightHO
        for(k = 0; k < NumOutput; k ++)
        {
          DeltaWeightHO[0][k] = eta * DeltaO[k] + alpha * DeltaWeightHO[0][k];
          WeightHO[0][k] += DeltaWeightHO[0][k];
          for(j = 0; j < NumHidden; j++)
          {
            // Ajuste do peso
//          DeltaWeightHO[j][k] = eta * Hidden[p][j] * DeltaO[k] + alpha * DeltaWeightHO[j][k];
            DeltaWeightHO[j][k] = eta * Hidden[p][j] * DeltaO[k];
            WeightHO[j][k] += DeltaWeightHO[j][k];
          }
        }

      } // Fim do laco de repeticao para os padroes de treinamento

      if(epoca%100 == 0)
      {
        fprintf(stdout, "\nEpoca %-5d :   Erro = %f", epoca, Erro);
        fprintf(CURVAERRO, "%f\n", Erro);
      }
      fprintf(FULLERRO, "%f\n", Erro);

      // Criterio de parada para quando 'aprender o suficiente'
      if(Erro < ErroStop)
      {
        fprintf(CURVAERRO, "%f\n", Erro);
        break;
      }

    } // Fim do laco de atualizacao dos pesos

    // Imprime os resultado de saida da rede
    fprintf(stdout, "\n\nDados finais do treinamento -> Epoca = %d; Erro = %f", epoca, Erro);
    for(p = 0; p < NumPattern; p++)
    {
      for(k = 0; k < NumOutput; k++)
      {
        fprintf(SAIDA, "%f ", Output[p][k]);
      }
      fprintf(SAIDA, "\n");
    }
    fprintf(stdout, "\n\nFinalizado!\n\n");

    // Salva os pesos WeightIH
    for(i = 0; i < NumInput; i++)
    {
      for(j = 0; j < NumHidden; j++)
      {
        fprintf(PESOS, "%3.40f ", WeightIH[i][j]);
      }
      fprintf(PESOS, "\n");
    }

      // Salva os pesos WeightHO
    for(j = 0; j < NumHidden; j++)
    {
      for(k = 0; k < NumOutput; k ++)
      {
        fprintf(PESOS, "%3.40f ", WeightHO[j][k]);
      }
      fprintf(PESOS, "\n");
    }

    // Fecha o arquivo
    fclose(CONFIG);
    fclose(ENTRADA);
    fclose(OBJETIVO);
    fclose(SAIDA);
    fclose(PESOS);
    fclose(CURVAERRO);
    fclose(FULLERRO);

    // Desalocando variaveis dinamicas
    free(ranpat);
    free(DeltaO);
    free(SumDOW);
    free(DeltaH);
    for (i = 0; i < NumPattern; i++)
    {
        free(Input[i]);
        free(Target[i]);
        free(SumH[i]);
        free(Hidden[i]);
        free(SumO[i]);
        free(Output[i]);
    }
    free(Input);
    free(Target);
    free(SumH);
    free(Hidden);
    free(SumO);
    free(Output);
    for (i = 0; i < NumInput; i++)
    {
        free(WeightIH[i]);
        free(DeltaWeightIH[i]);
    }
    free(WeightIH);
    free(DeltaWeightIH);
    for (i = 0; i < NumHidden; i++)
    {
        free(WeightHO[i]);
        free(DeltaWeightHO[i]);
    }
    free(WeightHO);
    free(DeltaWeightHO);
  }

////////////////////////////////////////////////////////////////////////
// Aplicacando uma rede ja treinada
////////////////////////////////////////////////////////////////////////
  else
  {
    // Avisa sobre a aplicacao da rede
    printf("\nAplicando a rede!!!\n\n");
    
    // Arquivo de dados
    ENTRADA = fopen("aplicInput.dat","r");
    if (ENTRADA == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao abrir arquivo de entrada.\n\n");
      return(1);
    }
    SAIDA = fopen("saidaAplic.dat","w+");
    if (SAIDA == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao criar arquivo de saida.\n\n");
      return(1);
    }
    PESOS = fopen("pesos.dat","r");
    if (PESOS == NULL)
    {
      fprintf(stderr,"ERRO: Falha ao abrir arquivo de pesos da rede.\n\n");
      return(1);
    }

    // Variaveis em uso
    int    i, j, k, p;
    float  Temp;
    double **Input, **SumH, **Hidden, **SumO, **Output, **WeightIH, **WeightHO;

    // Declaracao variaveis dinamicas
    Input = malloc(NumPattern*sizeof(double));
    SumH = malloc(NumPattern*sizeof(double));
    Hidden = malloc(NumPattern*sizeof(double));
    SumO = malloc(NumPattern*sizeof(double));
    Output = malloc(NumPattern*sizeof(double));
    for (i = 0; i < NumPattern; i++)
    {
        Input[i] = malloc(NumInput*sizeof(double));
        SumH[i] = malloc(NumHidden*sizeof(double));
        Hidden[i] = malloc(NumHidden*sizeof(double));
        SumO[i] = malloc(NumOutput*sizeof(double));
        Output[i] = malloc(NumOutput*sizeof(double));
    }
    WeightIH = malloc(NumInput*sizeof(double));
    for (i = 0; i < NumInput; i++)
    {
        WeightIH[i] = malloc(NumHidden*sizeof(double));
    }
    WeightHO = malloc(NumHidden*sizeof(double));
    for (i = 0; i < NumHidden; i++)
    {
        WeightHO[i] = malloc(NumOutput*sizeof(double));
    }

    // Le os dados dos arquivo de entrada para aplicacao
    for (p = 0; p < NumPattern; p++)
    {
      for (i = 0; i < NumInput; i++)
      {
        fscanf(ENTRADA, "%f", &Temp);
        Input[p][i] = (double)Temp;
      }
      //fprintf(stdout,"%f %f %f\n",Input[p][0],Input[p][1],Input[p][2]);
    }

    // Carrega WeightIH
    for(i = 0; i < NumInput; i++)
    {
      for(j =0; j < NumHidden ; j++)
      {
        fscanf(PESOS, "%f", &Temp);
        WeightIH[i][j] = (double)Temp;
      }
      //fprintf(stdout,"%f %f %f\n",WeightIH[i][0],WeightIH[i][1],WeightIH[i][2]);
    }

    // Carrega WeightHO
    for(j = 0; j < NumHidden; j ++)
    {
      for(k = 0; k < NumOutput; k++)
      {
        fscanf(PESOS, "%f", &Temp);
        WeightHO[j][k] = (double)Temp;
      }
      //fprintf(stdout,"%f %f \n",WeightHO[j][0],WeightHO[j][1]);
    }

    // Laco de repeticao para todos os padroes
    for(p = 0; p < NumPattern; p++)
    {
      // Calcula a ativacao das unidades escondidas
      for(j = 0; j < NumHidden; j++)
      {
        SumH[p][j] = WeightIH[0][j];
        for(i = 0; i < NumInput; i++)
        {
          SumH[p][j] += Input[p][i] * WeightIH[i][j];
        }
        Hidden[p][j] = 1.0/(1.0 + exp(-SumH[p][j]));
      }

      // Calcula a ativacao das unidades de saida
      for(k = 0; k < NumOutput; k++)
      {
        SumO[p][k] = WeightHO[0][k];
        for(j = 0; j < NumHidden; j++)
        {
          SumO[p][k] += Hidden[p][j] * WeightHO[j][k];
        }
        // Saida Sigmoidal
        Output[p][k] = 1.0/(1.0 + exp(-SumO[p][k]));
        // Saida Linear
//      Output[p][k] = SumO[p][k];
        //Grava o resultado em arquivo
        fprintf(SAIDA, "%f ", Output[p][k]);
      }
      fprintf(SAIDA, "\n");
    }

    // Fecha o arquivo
    fclose(CONFIG);
    fclose(ENTRADA);
    fclose(SAIDA);
    fclose(PESOS);

    // Desalocando variaveis dinamicas
    for (i = 0; i < NumPattern; i++)
    {
        free(Input[i]);
        free(SumH[i]);
        free(Hidden[i]);
        free(SumO[i]);
        free(Output[i]);
    }
    free(Input);
    free(SumH);
    free(Hidden);
    free(SumO);
    free(Output);
    for (i = 0; i < NumInput; i++)
    {
        free(WeightIH[i]);
    }
    free(WeightIH);
    for (i = 0; i < NumHidden; i++)
    {
        free(WeightHO[i]);
    }
    free(WeightHO);
  }

  return (0);

} // Fim da funcao principal
