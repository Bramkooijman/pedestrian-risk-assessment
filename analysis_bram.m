%% by Bram Kooijman <b.kooijman@student.tudelft.nl>, Pavlo Bazilinskyy <p.bazilinskyy@tudelft.nl>
clear variables;close all force;clc
opengl hardware % use OpenGL hardware for better figure quality
%% Read Excel files with raw data
%[~,~,raw_rt]=xlsread('keypress_data.xlsx','A1:HSL921'); % import Excel file with RT data from the Database
[~,~,headers]=xlsread('f1730370.xlsx','A1:BK1');
[~,~,raw_cf]=xlsread('f1730370.xlsx','A2:BK1238'); % import Excel file with Figure-Eight data
temp=raw_cf(:,9);Country=cell(size(raw_cf,1),1);for i=1:length(temp);try Country(i)=unique(temp(i));catch error;Country(i)={'NaN'};end;end % Country data from the Figure-Eight data
disp(['Number of respondents in the Figure Eight database = ' num2str(size(raw_cf,1))])
%disp(['Number of entries in the RT database = ' num2str(size(raw_rt,1))])
%% Process Figure-Eight data into the X matrix (1237 x 16 matrix)
temp=raw_cf(:,17);X(:,1)=strcmp(temp,'no')+2*strcmp(temp,'yes'); % Instructions understood
temp=raw_cf(:,35);X(:,2)=1*strcmp(temp,'female')+2*strcmp(temp,'male')-1*strcmp(temp,'i_prefer_not_to_respond'); % Gender
temp=raw_cf(:,34);for i=1:length(temp);try if strcmp(temp(i),'?');X(i,3)=NaN;else;X(i,3)= cell2mat(temp(i));end;catch error;X(i,3)=NaN;end;end % Age
X(X(:,3)>110,3)=NaN; % People who report age greater than 110 years
temp=raw_cf(:,16);for i=1:length(temp);try if strcmp(temp(i),'?');X(i,4)=NaN;else;X(i,4)= cell2mat(temp(i));end;catch error;X(i,4)=NaN;end;end % Age of obtaining driver's license
X(X(:,4)>110 | X(:,4)<15,4)=NaN; % People who report licence more than 110 years
temp=raw_cf(:,36);X(:,5)=1*strcmp(temp,'private_vehicle')+2*strcmp(temp,'public_transportation')+3*strcmp(temp,'motorcycle')+4*strcmp(temp,'walkingcycling')+5*strcmp(temp,'other')-1*strcmp(temp,'i_prefer_not_to_respond');  % Primary mode of transportation
temp=raw_cf(:,31);X(:,6)=1*strcmp(temp,'never')+2*strcmp(temp,'less_than_once_a_month')+3*strcmp(temp,'once_a_month_to_once_a_week')+4*strcmp(temp,'1_to_3_days_a_week')+5*strcmp(temp,'4_to_6_days_a_week')+6*strcmp(temp,'every_day')-1*strcmp(temp,'i_prefer_not_to_respond'); % How many times in past 12 months did you drive a vehicle
temp=raw_cf(:,13);for i=1:length(temp);try X(i,7)=1+cell2mat(temp(i));catch error;X(i,7)=1*strcmp(temp(i),'0_km__mi')+2*strcmp(temp(i),'1__1000_km_1__621_mi')+3*strcmp(temp(i),'1001__5000_km_622__3107_mi')+4*strcmp(temp(i),'5001__15000_km_3108__9321_mi')+5*strcmp(temp(i),'15001__20000_km_9322__12427_mi')+6*strcmp(temp(i),'20001__25000_km_12428__15534_mi')+7*strcmp(temp(i),'25001__35000_km_15535__21748_mi')+8*strcmp(temp(i),'35001__50000_km_21749__31069_mi')+9*strcmp(temp(i),'50001__100000_km_31070__62137_mi')+10*strcmp(temp(i),'more_than_100000_km_more_than_62137_mi')-1*strcmp(temp(i),'i_prefer_not_to_respond');end;end % Mileage
temp=raw_cf(:,19);for i=1:length(temp);try X(i,8)=1+cell2mat(temp(i));catch error;X(i,8)=7*strcmp(temp(i),'more_than_5')-1*strcmp(temp(i),'i_prefer_not_to_respond');end;end % Number of accidents
temp=raw_cf(:,20:26);X(:,9:15)=1*strcmp(temp,'0_times_per_month')+2*strcmp(temp,'1_to_3_times_per_month')+3*strcmp(temp,'4_to_6_times_per_month')+4*strcmp(temp,'7_to_9_times_per_month')+5*strcmp(temp,'10_or_more_times_per_month')-1*strcmp(temp,'i_prefer_not_to_respond'); % Driving behaviour DBQ
temp=raw_cf(:,30);for i=1:length(temp);try if strcmp(temp(i),'?'); X(i,16)=NaN;else;X(i,16)=cell2mat(temp(i));end;catch error;X(i,16)=NaN;end;end % in_which_year_do_you_think_that_most_cars_will_be_able_to_drive_fully_automatically_in_your_country_of_residence
temp=find(X(:,16)<2018);X(temp,16)=NaN; % People who report a number less than 2014
%temp=raw_cf(:,33);X(:,17)=temp; %Worker codes of the people

for i=1:size(raw_cf,1);X(i,21)=24*3600*(datenum(raw_cf{i,2})-datenum(raw_cf{i,4}));end %% Compute survey time and store in the 21th column of the X matrix
X(:,22)=tiedrank(X(:,21))./size(X,1); % ranking the survey time
X(X<=0)=NaN; % Put missing values (0) or no response (-1) at NaN
X(isnan(sum(X(:,9:15),2)),9:15)=NaN; % for the DBQ put all 7 items at NaN if any of the 7 items is NaN
X(:,9:15)=tiedrank(X(:,9:15))./repmat(sum(~isnan(X(:,9:15))),size(X,1),1); % ranking of DBQ scores so that these scores become comparable between surveys
%% Extract participant IDs from Figure-Eight data
X(:,18)=cell2mat(raw_cf(:,1)); % Store Figure-Eight ID in the 18th column
% for i=1:size(raw_cf,1)
%     id_str = raw_cf{i,57};
%     X(i,19) = str2double(id_str(regexp(id_str,'DANGER')+6:end));
% end

%% Filter data based on the folllowing criteria:
%1. People who did not read instructions.
%2. People that are under 18 years of age.
%3. People who completed the study in under 5 min.
%4. People who completed the study from the same IP more than once
               %(the 1st data entry is retained).
%5. People who used the same `worker_code` multiple times.
               %(the 1st data entry is retained).
            
invalid1 = find(X(:,1)==1); % respondents who did not read instructions
invalid2 = find(X(:,3)<18); % respondents who indicated they are under 18 years old
invalid3 = find(X(:,21)< 300); % respondents who completed the study within 5 minutes

%% Find rows with identical ip adresses
y = NaN(size(X(:,1)));
IPCF=NaN(size(raw_cf,1),1);
for i=1:size(raw_cf,1)
    try IPCF(i)=str2double(strrep(raw_cf(i,12),'.',''));
    catch
        IPCF(i)=cell2mat(raw_cf(i,12));
    end
end % reduce IP addresses of Figure-Eight to a single number
for i=1:size(X,1)
    temp=find(IPCF==IPCF(i));
    if length(temp)==1 % if the IP address occurs only once
        y(i)=1; % keep
    elseif length(temp)>1 % if the IP addres occurs more than once
        y(temp(1))=1; % keep the first survey for that IP address
        y(temp(2:end))=2; % no not keep the other ones
    end
end
invalid4=find(y>1); % respondents who completed the survey more than once (i.e., remove the doublets)

%% Find double worker codes in the data
%transfer cell data to array of strings
y=NaN(size(raw_cf(:,33)));
WCCF=strings(size(raw_cf(:,33)));
for i=1:size(raw_cf(:,33),1)
   WCCF(i)=string(raw_cf(i,33));
end
for i=1:size(X,1)
    temp=find(WCCF==WCCF(i));
    if length(temp)==1 % if the IP address occurs only once
        y(i)=1; % keep
    elseif length(temp)>1 % if the IP addres occurs more than once
        y(temp(1))=1; % keep the first survey for that IP address
        y(temp(2:end))=2; % no not keep the other ones
    end
end
cheaters=find(y>1);

%% Create table of cheaters

%Create array of all rows which are cheaters
cheaters=unique(cheaters);

%Fill cheater matrix with data of all cheaters
cf_cheaters(1,:)=headers;
for i=(1:size(cheaters))
    cheater_row=cheaters(i); 
    cf_cheaters(i+1,:)=raw_cf(cheater_row,:);
end

% Convert cells to table
cheater_table = cell2table(cf_cheaters);
 
% Write the table to a CSV file
writetable(cheater_table,'f1730370_cheaters.csv','WriteVariableNames',0);

%% Remove invalid data from main matrix and create a new one

invalid_data=[invalid1;invalid2;invalid3;invalid4;cheaters];
invalid_data=unique(invalid_data);