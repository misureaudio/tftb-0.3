function probe_tfrview
%PROBE_TFRVIEW  Confirm A1 fixed: tfrview no longer raises the version error.
addpath('D:/TOOLBOX/tftb-0.3/mfiles');
N=128; sig=fmlin(N); t=1:N;
tfr=tfrwv(sig);
% tfrview(tfr,sig,t,method,param) ; method=1 (contour) minimal
try
  tfrview(tfr,sig,t,1,[1 0 0 10 128 3 0 0 0]);
  fprintf('tfrview: COMPLETED without error\n');
catch ME
  fprintf('tfrview -> %s\n', ME.identifier);
  fprintf('   %s\n', ME.message);
  if ~isempty(ME.stack), fprintf('   at %s line %d\n', ME.stack(1).file, ME.stack(1).line); end
  if contains(ME.message,'unsupported matlab version')
    fprintf('   *** A1 STILL PRESENT ***\n');
  else
    fprintf('   *** version error GONE (A1 fixed) ***\n');
  end
end
end
