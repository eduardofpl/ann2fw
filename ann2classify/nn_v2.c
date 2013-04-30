// Para treinar com muitas linhas, nao esquecer de aumentar o stack:
// $ ulimit -s unlimited

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <fcntl.h>
#include"ran3.c"

// Parametros globais (e fixos)
#define TRAIN 0
#define NUMPAT 2500
#define NUMIN  3
#define NUMHID 3
#define NUMOUT 2

// Ponteiro para arquivo
FILE *ENTRADA = NULL;
FILE *OBJETIVO = NULL;
FILE *SAIDA = NULL;
FILE *PESOS = NULL;
FILE *CURVAERRO = NULL;
FILE *FULLERRO = NULL;

// Prototipo da funcao de geracao de numeros aleatorios
float ran3(long *idum);

// Funcao principal
int main(void)
{

  if (TRAIN == 1)
  {
    // Avisa sobre o treinamento da rede
    printf("\nTreinando a rede!!!\n");

    // Arquivo de dados
    ENTRADA = fopen("trainInput.dat","r");
    if (ENTRADA == NULL)
    {
      fprintf(stderr,"Falha ao abrir arquivo de entrada.");
      return(1);
    }
    OBJETIVO = fopen("trainOutput.dat","r");
    if (OBJETIVO == NULL)
    {
      fprintf(stderr,"Falha ao abrir arquivo de objetivos.");
      return(1);
    }
    SAIDA = fopen("saidaTreina.dat","w+");
    if (SAIDA == NULL)
    {
      fprintf(stderr,"Falha ao criar arquivo de saida.");
      return(1);
    }
    PESOS = fopen("pesos.dat","w+");
    if (PESOS == NULL)
    {
      fprintf(stderr,"Falha ao criar arquivo de pesos.");
      return(1);
    }
    CURVAERRO = fopen("curvaErro.dat","w+");
    if (CURVAERRO == NULL)
    {
      fprintf(stderr,"Falha ao criar arquivo de curva de erro.");
      return(1);
    }
    FULLERRO = fopen("fullErro.dat","w+");
    if (FULLERRO == NULL)
    {
      fprintf(stderr,"Falha ao criar arquivo de erro completo.");
      return(1);
    }

    // Variaveis em uso
    int    i, j, k, p, np, op, ranpat[NUMPAT], epoca;
    int    NumPattern = NUMPAT, NumInput = NUMIN, NumHidden = NUMHID, NumOutput = NUMOUT;
    long   seed, *idum;
    float  Temp;
    double Input[NUMPAT][NUMIN];
    double Target[NUMPAT][NUMOUT];
    double SumH[NUMPAT][NUMHID], WeightIH[NUMIN][NUMHID], Hidden[NUMPAT][NUMHID];
    double SumO[NUMPAT][NUMOUT], WeightHO[NUMHID][NUMOUT], Output[NUMPAT][NUMOUT];
    double DeltaO[NUMOUT], SumDOW[NUMHID], DeltaH[NUMHID];
    double DeltaWeightIH[NUMIN][NUMHID], DeltaWeightHO[NUMHID][NUMOUT];
    double Erro, Ece, Esse, Omega;
    int    MaxEpoca = 1000;
    double eta = 0.3, alpha = 0.2, smallwt = 0.5, ErroStop = 0.00001;

    // Le os dados dos arquivos
    for (i = 0; i < NUMPAT; i++)
    {
      for (j = 0; j < NUMIN; j++)
      {
        fscanf(ENTRADA, "%g", &Temp);
        Input[i][j] = (double)Temp;
      }
      for (j = 0; j < NUMOUT; j++)
      {
        fscanf(OBJETIVO, "%g", &Temp);
        Target[i][j] = (double)Temp;
      }
    }

    // Semente geradora de numeros aleatorios
    seed = -25L;
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
          // Saida Linear, SSE
  //      DeltaO[k] = Target[p][k] - Output[p][k];
        }

        //Nao faz a ultima das ultimas atualizacoes
        if ((epoca == MaxEpoca-1) && (np == NumPattern-1))
        {
          fprintf(stdout,"\n\nFim do treinamento.\n\n");
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
    fprintf(stdout, "\n\nDADOS FINAIS DA REDE -> EPOCA = %d - ERRO = %f", epoca, Erro);
  /*fprintf(stdout, "\n\nDADOS FINAIS DA REDE -> EPOCA = %d - ERRO = %f\n\nPadrao\t", epoca, Erro);
    for(i = 1; i <= NumInput; i++)
    {
      fprintf(stdout, "Entrada%-4d\t", i);
    }
    for(k = 1; k <= NumOutput; k++)
    {
      fprintf(stdout, "Objetivo%-4d\tSaida%-4d\t", k, k);
    } */
    for(p = 0; p < NumPattern; p++)
    {
  /*    fprintf(stdout, "\n%d\t", p);
      for(i = 1; i <= NumInput; i++)
      {
        fprintf(stdout, "%f\t", Input[p][i]);
      } */
      for(k = 0; k < NumOutput; k++)
      {
  //      fprintf(stdout, "%f\t%f\t", Target[p][k], Output[p][k]);
        fprintf(SAIDA, "%f ", Output[p][k]);
      }
      fprintf(SAIDA, "\n");
    }
    fprintf(stdout, "\n\nFinalizado!\n\n");

    // Salva os pesos WeightIH
    //fprintf(PESOS, "Pesos: Entrada -> Escondida\n");
    for(i = 0; i < NumInput; i++)
    {
      for(j = 0; j < NumHidden; j++)
      {
        fprintf(PESOS, "%3.40f ", WeightIH[i][j]);
      }
      fprintf(PESOS, "\n");
    }

      // Salva os pesos WeightHO
    //fprintf(PESOS, "Pesos: Escondida -> Saida\n");
    for(j = 0; j < NumHidden; j++)
    {
      for(k = 0; k < NumOutput; k ++)
      {
        fprintf(PESOS, "%3.40f ", WeightHO[j][k]);
      }
      fprintf(PESOS, "\n");
    }

    // Fecha o arquivo
    fclose(ENTRADA);
    fclose(OBJETIVO);
    fclose(SAIDA);
    fclose(PESOS);
    fclose(CURVAERRO);
    fclose(FULLERRO);

  }
  else
  {
    // Avisa sobre a aplicacao da rede
    printf("\nAplicando a rede!!!\n\n");
    
    // Arquivo de dados
    ENTRADA = fopen("aplicInput.dat","r");
    if (ENTRADA == NULL)
    {
      fprintf(stderr,"Falha ao abrir arquivo de entrada.");
      return(1);
    }
    SAIDA = fopen("saidaAplic.dat","w+");
    if (SAIDA == NULL)
    {
      fprintf(stderr,"Falha ao criar arquivo de saida.");
      return(1);
    }
    PESOS = fopen("pesos.dat","r");
    if (PESOS == NULL)
    {
      fprintf(stderr,"Falha ao abrir arquivo de pesos da rede.");
      return(1);
    }

    // Variaveis em uso
    int    i, j, k, p;
    int    NumPattern = NUMPAT, NumInput = NUMIN, NumHidden = NUMHID, NumOutput = NUMOUT;
    float  Temp;
    double Input[NUMPAT][NUMIN];
    double SumH[NUMPAT][NUMHID], WeightIH[NUMIN][NUMHID], Hidden[NUMPAT][NUMHID];
    double SumO[NUMPAT][NUMOUT], WeightHO[NUMHID][NUMOUT], Output[NUMPAT][NUMOUT];
    double DeltaO[NUMOUT];

    // Le os dados dos arquivo de entrada para aplicacao
    for (p = 0; p < NUMPAT; p++)
    {
      for (i = 0; i < NUMIN; i++)
      {
        fscanf(ENTRADA, "%g", &Temp);
        Input[p][i] = (double)Temp;
      }
      //fprintf(stdout,"%f %f %f\n",Input[p][0],Input[p][1],Input[p][2]);
    }

    // Carrega WeightIH
    for(i = 0; i < NumInput; i++)
    {
      for(j =0; j < NumHidden ; j++)
      {
        fscanf(PESOS, "%g", &Temp);
        WeightIH[i][j] = (double)Temp;
      }
      //fprintf(stdout,"%f %f %f\n",WeightIH[i][0],WeightIH[i][1],WeightIH[i][2]);
    }

    // Carrega WeightHO
    for(j = 0; j < NumHidden; j ++)
    {
      for(k = 0; k < NumOutput; k++)
      {
        fscanf(PESOS, "%g", &Temp);
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
    fclose(ENTRADA);
    fclose(SAIDA);
    fclose(PESOS);
  }

  return (0);

} // Fim da funcao principal

