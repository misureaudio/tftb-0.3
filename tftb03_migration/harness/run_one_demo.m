function run_one_demo(demo)
%RUN_ONE_DEMO  Run one tftb demo headless (shims on path, cwd = demos dir).
% NB: genpath('D:/...') is broken in R2024a (returns empty for forward-
% slash roots), so add the toolbox subdirectories explicitly.
addpath('D:/TOOLBOX/tftb-0.3/mfiles');
addpath('D:/TOOLBOX/tftb-0.3/tests');
addpath('D:/TOOLBOX/tftb-0.3/demos');
addpath('D:/TOOLBOX/tftb-0.3/data');
cd('D:/TOOLBOX/tftb-0.3/demos');
feval(demo);
close all;
fprintf('DEMO_DONE %s\n', demo);
end
