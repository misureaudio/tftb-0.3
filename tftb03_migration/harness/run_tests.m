function run_tests
%RUN_TESTS  Per-test isolation runner for tftb 0.2 unit tests on R2024a.
% Each test runs inside run_one (a separate function) so that a test
% SCRIPT's `clear;` wipes only run_one's workspace, never the orchestrator
% loop state. Prints one TSV line per test:
%   PASS|FAIL  name  errId  file  line  message
% plus BEGIN/END markers so console warnings can be attributed.

  TFTB = 'D:/TOOLBOX/tftb-0.3';
  addpath(fullfile(TFTB,'mfiles'));
  addpath(fullfile(TFTB,'tests'));
  addpath(fullfile(TFTB,'demos'));
  addpath(fullfile(TFTB,'data'));

  files = dir(fullfile(TFTB,'tests','*.m'));
  names = {files.name};
  names = cellfun(@(x) x(1:end-2), names, 'uni', false);
  keep = ~strcmp(names,'testall') & ~strcmp(names,'layoutst') & ~strcmp(names,'lineplot');
  % testall re-runs everything; layoutst is a pure GUI menu loop (menu())
  % and cannot run headless. lineplot is a helper FUNCTION (not a test)
  % used by htlt; the harness runs every file via feval, which errors on a
  % no-arg function call, so it must be excluded.
  names = names(keep);

  n = 0; npass = 0; nfail = 0;
  for i = 1:numel(names)
    name = names{i};
    close all;                       % release any figure from the previous test
    rng(0);                          % 0.3: deterministic RNG for every test,
    % so noisecg-based sub-tests are reproducible and order-independent
    % (a test's internal clear/rng would otherwise leave later tests with a
    % shifted state). This makes the suite a trustworthy gate.
    fprintf('BEGIN_TEST %s\n', name);
    try
      run_one(name);
      fprintf('PASS\t%s\n', name);
      npass = npass + 1;
    catch ME
      f = ''; l = '';
      if ~isempty(ME.stack)
        f = ME.stack(1).file;
        l = num2str(ME.stack(1).line);
      end
      msg = strrep(ME.message, char(9), ' ');
      msg = strrep(msg, char(10), ' ');
      fprintf('FAIL\t%s\t%s\t%s\t%s\t%s\n', name, ME.identifier, f, l, msg);
      nfail = nfail + 1;
    end
    fprintf('END_TEST %s\n', name);
  end
  fprintf('SUMMARY total=%d pass=%d fail=%d\n', n, npass, nfail);
end

function run_one(name)
  % Runs in its own workspace; a script's `clear;` wipes only this.
  feval(name);
end
