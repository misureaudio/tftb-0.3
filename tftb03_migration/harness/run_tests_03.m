function run_tests_03
%RUN_TESTS_03  Per-test isolation runner for tftb-0.3 unit tests.
TFTB = 'D:/TOOLBOX/tftb-0.3';
addpath(fullfile(TFTB,'mfiles'));
addpath(fullfile(TFTB,'tests'));
addpath(fullfile(TFTB,'demos'));
addpath(fullfile(TFTB,'data'));

files = dir(fullfile(TFTB,'tests','*.m'));
names = {files.name};
names = cellfun(@(x) x(1:end-2), names, 'uni', false);
keep = ~strcmp(names,'testall') & ~strcmp(names,'layoutst') & ~strcmp(names,'lineplot');
% testall re-runs everything; layoutst is a pure GUI menu loop; lineplot
% is a HELPER function (rho,theta,M,N), not a test.
names = names(keep);

n = 0; npass = 0; nfail = 0;
for i = 1:numel(names)
  name = names{i};
  close all;
  fprintf('BEGIN_TEST %s\n', name);
  try
    run_one(name);
    fprintf('PASS\t%s\n', name);
    npass = npass + 1;
  catch ME
    f=''; l='';
    if ~isempty(ME.stack), f=ME.stack(1).file; l=num2str(ME.stack(1).line); end
    msg = strrep(ME.message, char(9),' '); msg = strrep(msg, char(10),' ');
    fprintf('FAIL\t%s\t%s\t%s\t%s\t%s\n', name, ME.identifier, f, l, msg);
    nfail = nfail + 1;
  end
  close all;
  fprintf('END_TEST %s\n', name);
end
fprintf('SUMMARY total=%d pass=%d fail=%d\n', n, npass, nfail);
end
function run_one(name)
  feval(name);
end
