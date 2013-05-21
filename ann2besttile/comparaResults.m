close all;
clear all;
clc;

verdade = load('trainOutput.dat');
estimado = load('saidaTreina.dat');
% verdade = load('verdadeOutput.dat');
% estimado = load('saidaAplic.dat');

inst = size(verdade,1);
pontos = size(verdade,2);

selecionado = zeros(inst,pontos);

certo = 0;
errado = 0;

for i=1:inst
   winner =  find(estimado(i,:)==max(estimado(i,:)));
   selecionado(i,winner) = 1.0;
   if (selecionado(i,:)==verdade(i,:))
       certo = certo + 1;
   else
       errado = errado + 1;
   end
end

fprintf('Acerto: %d (%f%%)\n',certo,certo/inst);
fprintf('Erro: %d (%f%%)\n',errado,errado/inst);

dlmwrite('selecionados.dat', selecionado, 'delimiter', ' ', 'precision', '%1.1f');