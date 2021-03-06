% Limpa o ambiente
close all;
clear all;
clc;

% Define o tamanho da imagem
sizeY = 50;
sizeX = 50;

% Dados de classificacao da rede neural
classified = 'saidaAplicArea.dat.case1';

% Vamos comparar com alguma verdade? 1 - SIM ; 0 - NAO
comparaVerdade = 1;

% Carrega os dados do(s) arquivo(s)
data = load(classified);
if (comparaVerdade == 1)
    % Se formos comparar a verdade carregamos tambem e preparamos variaveis
    verdade = 'verdadeOutputArea.dat.case1';
    dataVerdade = load(verdade);
    finalClass = zeros(1,sizeY*sizeX,'uint8');
    acertoClass = 0;
    erroClass = 0;
end

% Definicao do limite para atribuicao de classe (0.5 eh padrao)
eta = 0.5;
eta_c = 1.0 - eta;

% Prepara as variaveis
matrixF = zeros(sizeX,sizeY,'uint8');
matrixNF = zeros(sizeX,sizeY,'uint8');
matrixTot = zeros(sizeX,sizeY,'uint8');
matrixRGB = zeros(sizeX,sizeY,3,'uint8');

% Carrega os dados em matrizes prontas para serem plotadas
row = 0;
for x=1:sizeX
    for y=1:sizeY
        row = row + 1;
        matrixF(x,y) = uint8(data(1,row)*255.0);
        matrixNF(x,y) = uint8(data(1,row)*255.0);
        if (data(1,row) >= eta)
            matrixTot(x,y) = uint8(((data(1,row)-eta)/(1.0-eta))*255.0);
            matrixRGB(x,y,:) = [0, 255, 0];
            finalClass(1,row) = 1;
        else
            matrixTot(x,y) = uint8((data(1,row)-eta_c)/(1.0-eta_c)*255.0);
            matrixRGB(x,y,:) = [255, 0, 0];
            finalClass(1,row) = 0;
        end
        if (comparaVerdade == 1)
            if (finalClass(1,row) == uint8(dataVerdade(1,row)))
                acertoClass = acertoClass + 1;
            else
                erroClass = erroClass + 1;
            end
        end
    end
end

% Plota a certeza para a classe floresta
figure1a = figure();
set(figure1a, 'Position', [0 0 800 600]);
colormap('gray');
image(matrixF);
imwrite(matrixF,'image1.png','png');

% Plota a certeza para a classe nao-floresta
figure2a = figure();
set(figure2a, 'Position', [0 0 800 600]);
colormap('gray');
image(matrixNF);
imwrite(matrixNF,'image2.png','png');

% Plota a certeza conjunta
figure3a = figure();
set(figure3a, 'Position', [0 0 800 600]);
colormap('gray');
image(matrixTot);
imwrite(matrixTot,'image3.png','png');

% Plota a imagem classificada
figure4a = figure();
set(figure4a, 'Position', [0 0 800 600]);
image(matrixRGB);
imwrite(matrixRGB,'image4.png','png');

% Imprime no terminal o percentual de verdade se estivermos comparando
if (comparaVerdade == 1)
    fprintf('\nTotal de acertos: %d (%f%%)\n',acertoClass,acertoClass/(sizeX*sizeY));
    fprintf('Total de erros: %d (%f%%)\n\n',erroClass,erroClass/(sizeX*sizeY));
end
