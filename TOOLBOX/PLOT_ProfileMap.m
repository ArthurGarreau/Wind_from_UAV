% -*- encoding: utf-8       %
% author : Arthur GARREAU   %
% Date: 06.2020             %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% PLOT THE PROFILE ON A GOOGLE MAP (NEED API IDENTIFIANT) AND THE ALTITUDE
% OF THE DRONE WITH TIME 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%


aux = who('PHANTOM') ; % test whether PHANTOM or MAVIC data are present 

if  isempty(aux) == 0 %PHANTOM case
    DRONE = PHANTOM;
elseif isempty(aux) == 1 %MAVIC case
    DRONE = MAVIC;
end

addpath(genpath([PATH.TOOLS '/GoogleMap']))

%  API
%plot_google_map('APIKey', '') % You only need to run this once, which will store the API key in a mat file for all future usages


%% Plotting 

   

% Find the indices corresponding to the time range
time_indices = DRONE.time >= start_data & DRONE.time <= end_data;

time = DRONE.time(time_indices);
H = DRONE.GPS_Height(time_indices);
latGPS = DRONE.GPS_Lat(time_indices); 
lonGPS = DRONE.GPS_Lon(time_indices);


% % Remove the values equal to zero when the GPS is not detecting signal
% a = find(latGPS ~= 0 & latGPS > 70 & latGPS < 80);  
% latGPS = latGPS(a); lonGPS = lonGPS(a); H = H(a) ; Time = Time(a) ; 


figure('Position', [5 5 550 900])

subplot(211)
plot3(lonGPS,latGPS,H,'r','LineWidth',1)  

xlim([lonGPS(1)-0.13 lonGPS(1)+0.13])
zlim([0 max(H)+1])
plot_google_map('MapType', 'satellite')
title(datestr(time(1)))


subplot(212)

plot(time, H,'r', 'LineWidth', 1.5) 
datetick('x', 'HH:MM:SS')
xlabel('Time', 'Fontsize', 14)
ylabel('Height (m)', 'Fontsize', 14)
grid on ;

if save == true 
exportgraphics(gcf , [PATH.SAVE '/Map_' start_data(5:13) 'h' start_data(15:16) '.png'], 'Resolution', 600)
end 
