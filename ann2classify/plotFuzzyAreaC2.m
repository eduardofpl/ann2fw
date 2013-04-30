% Limpa o ambiente
close all;
clear all;
clc;

% Define o tamanho da imagem
sizeY = 20;
sizeX = 20;

% Dados de classificacao da rede neural
classified = 'saidaAplic.dat';

% Vamos comparar com alguma verdade? 1 - SIM ; 0 - NAO
comparaVerdade = 1;

% Carrega os dados do(s) arquivo(s)
data = load(classified);
if (comparaVerdade == 1)
    % Se formos comparar a verdade carregamos tambem e preparamos variaveis
    verdade = 'verdadeOutput.dat';
    dataVerdade = load(verdade);
    finalClass = zeros(1,sizeY*sizeX,'uint8');
    acertoClass = 0;
    erroClass = 0;
    matrixVerdade = zeros(sizeX,sizeY,3,'uint8');
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
row = 1;
for x=1:sizeX
    for y=1:sizeY
        matrixF(x,y) = uint8(data(1,row)*255.0);
        matrixNF(x,y) = uint8(data(1,row)*255.0);
        if (data(1,row) >= eta)
            matrixTot(x,y) = uint8(((data(1,row)-eta)/(1.0-eta))*255.0);
            matrixRGB(x,y,:) = [0, 255, 0];
            finalClass(1,row) = 1;
            finalClass(1,row+1) = 0;
        else
            matrixTot(x,y) = uint8((data(1,row)-eta_c)/(1.0-eta_c)*255.0);
            matrixRGB(x,y,:) = [255, 0, 0];
            finalClass(1,row) = 0;
            finalClass(1,row+1) = 1;
        end
        if (comparaVerdade == 1)
            if (finalClass(1,row) == uint8(dataVerdade(1,row)))
                acertoClass = acertoClass + 1;
            else
                erroClass = erroClass + 1;
            end
            if (uint8(dataVerdade(1,row)) == 1)
                matrixVerdade(x,y,:) = [0, 255, 0];
            else
                matrixVerdade(x,y,:) = [255, 0, 0];
            end
        end
        row = row + 2;
    end
end

% Plota a certeza para a classe floresta
figure1a = figure();
set(figure1a, 'Position', [0 0 800 600]);
colormap('gray');
image(matrixF);
imwrite(matrixF,'image1.png','png');


% % Plota a certeza para a classe nao-floresta
% figure2a = figure();
% set(figure2a, 'Position', [0 0 800 600]);
% colormap('gray');
% image(matrixNF);
% imwrite(matrixNF,'image2.png','png');
% 
% % Plota a certeza conjunta
% figure3a = figure();
% set(figure3a, 'Position', [0 0 574 604]);
% colormap('gray');
% image(matrixTot);
% imwrite(matrixTot,'image3.png','png');
% 
% % Plota a imagem classificada
% figure4a = figure();
% set(figure4a, 'Position', [0 0 574 604]);
% image(matrixRGB);
% imwrite(matrixRGB,'image4.png','png');
% 
% % Imprime no terminal o percentual de verdade se estivermos comparando
% if (comparaVerdade == 1)
%     fprintf('\nTotal de acertos: %d (%f%%)\n',acertoClass,acertoClass/(sizeX*sizeY));
%     fprintf('Total de erros: %d (%f%%)\n\n',erroClass,erroClass/(sizeX*sizeY));
%     % Plota a imagem verdade
%     figure5a = figure();
%     set(figure5a, 'Position', [0 0 800 600]);
%     image(matrixVerdade);
%     imwrite(matrixVerdade,'image5.png','png');
% end
