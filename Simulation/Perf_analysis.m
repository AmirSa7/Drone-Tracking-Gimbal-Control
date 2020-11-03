[~,~,pos_info] = xlsread("D:\Technion\Control Systems Project\Code\yolov5\ramp_location_info.csv");
[~,~,diff_info] = xlsread("D:\Technion\Control Systems Project\Code\yolov5\ramp_diff_info.csv");

pos_info = cell2mat(pos_info);
diff_info = cell2mat(diff_info);

pos_info = pos_info(:,[10:end-10]);
diff_info = diff_info(:,[10:end-10]);


t_pos = pos_info(1, :);
target_pos = pos_info(2, :);
gimbal_pos = pos_info(3, :);



t_diff = diff_info(1, :);
measured_diff = diff_info(2, :);
est_diff = diff_info(3, :);

figure(); hold on;
plot(t_pos, target_pos);
plot(t_pos, gimbal_pos);
legend('target pos', 'gimbal pos');

figure(); hold on;
plot(t_diff, measured_diff);
plot(t_diff, est_diff);
legend('measured diff', 'estimated diff');

MSE_measured = sum(measured_diff.^2)/length(measured_diff)
MSE_estimated = sum(est_diff.^2)/length(est_diff)
