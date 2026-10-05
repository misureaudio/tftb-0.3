% RUN_DEMOS  Headless execution of the 7 tftb demos on R2024a.
% Each demo runs in its own MATLAB process (one -batch call) so a failure
% or hang in one demo cannot kill the rest. Shims (pause/input/menu) in
% this harness dir shadow the built-ins for demo code (cwd = demos dir).
function run_demos
demos = {'tfdemo1','tfdemo2','tfdemo3','tfdemo4','tfdemo5','tfdemo6','tfdemo7'};
for i = 1:numel(demos)
  d = demos{i};
  cmd = sprintf('addpath(''D:/Source/hermes-dir/tftb03_migration/harness''); run_one_demo(''%s'')', d);
  fprintf('BEGIN_DEMO %s\n', d);
  [st, out] = system(['matlab -batch "' cmd '" 2>&1']);
  lines = strsplit(strrep(out, char(13), ''), char(10));
  keep = lines(~cellfun(@isempty, lines));
  % drop JVM noise (e.g. "Picked up JAVA_TOOL_OPTIONS: ..." is sometimes
  % printed AFTER the demo's final line, so DEMO_DONE is not keep(end))
  keep = keep(~cellfun(@(s) ~isempty(strfind(s,'JAVA_TOOL_OPTIONS')), keep));
  % PASS = clean exit + DEMO_DONE present among the final lines (robust to
  % the JVM trailing-noise ordering); a MATLAB error aborts before DEMO_DONE.
  tailN = keep(max(1,numel(keep)-4):numel(keep));
  hasDone = any(cellfun(@(s) ~isempty(strfind(s,'DEMO_DONE')), tailN));
  if st == 0 && ~isempty(keep) && hasDone,
    fprintf('PASS\t%s\n', d);
  else
    tail = strjoin(keep(end-min(15,numel(keep)):end), ' | ');
    fprintf('FAIL\t%s\tstatus=%d\ttail=%s\n', d, st, tail);
  end
  fprintf('END_DEMO %s\n', d);
end
fprintf('DEMOS_DONE\n');
end
