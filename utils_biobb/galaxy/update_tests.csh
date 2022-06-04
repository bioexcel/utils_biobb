#!/bin/csh
set root_dir=$1
set galaxy=`pwd`
set test_data=$galaxy/test-data
cd $root_dir
foreach f (biobb*)
  if (-e $f/$f/test) then
    rsync -av --exclude=config $root_dir/$f/$f/test/data/ $test_data/$f
    rsync -av $root_dir/$f/$f/test/reference/ $test_data/$f
  endif
end
cd $galaxy

