close all;
clear all;
clc;

result = load('saidaAplic.dat');
taskID = load('aplicTasks.dat');

number = size(result,1);

sumResults = sum(result(:,:),2);
maxValue = max(result(:,:),[],2);
compare = zeros(number,3);
compare(:,1) = taskID;
compare(:,2) = sumResults;
compare(:,3) = maxValue;

up1 = 0;
les0 = 0;
for i = 1:number
    if sumResults(i) > 1.0
        up1 = up1 + 1;
    end
    if sumResults(i) < 0.0
        les0 = les0 + 1;
    end
end
