delta = 1/30;
pulse_len = 100;
speed_factor = 38000;
null_speed_delay = 200;
degs_per_step = 0.025;

A = [1 delta delta^2/2;
     0   1     delta;
     0   0       1];
 
B = [0; 0; 0];
 
C = [1 0 0];

D = 0;

A_cont = [0   1   0;
          0   0   1;
          0   0   0];

sys = ss(A,[],C,[], delta);

W = [0 0 0;
     0 0 0;
     0 0 10];

%W = [delta^2/4     delta^3/3     delta^2/2;
%     delta^3/3     delta^2       delta;
%     delta^2/2      delta        1];
 
V = 0.05;

x_init = [3 3 3]';

[X, K, L] = icare(A_cont', C', W, V, [], [], []);

for delta = [1/10, 1/20, 1/30, 1/40, 1/50, 1/60]
     A = [1 delta delta^2/2;
     0   1     delta;
     0   0       1];
    [X2, K2, L2] = idare(A', C', W, V, [], eye(3));
    disp(K2);
end