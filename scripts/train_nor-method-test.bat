set train_data="./data/train_data/basic/train_data/mean_group0_dist3000.h5"
set SEfile="./data/train_data/basic/SE_data/group0/SE.txt"

set output_folder_root="./output/nor-method-test/raw"
python train.py --time_slot 1440 --num_his 5 --num_pred 1 --batch_size 24 ^
        --max_epoch 100 --patience 100 --learning_rate 0.01 ^
        --normalization_method raw ^
        --traffic_file %train_data% ^
        --SE_file %SEfile% ^
        --model_file %output_folder_root%/model.pkl ^
        --log_file %output_folder_root%/log.txt ^
        --output_folder %output_folder_root% ^
        --device gpu

@REM set output_folder_root="./output/nor-method-test/z-score"
@REM python train.py --time_slot 1440 --num_his 5 --num_pred 1 --batch_size 24 ^
@REM         --max_epoch 100 --patience 100 --learning_rate 0.01 ^
@REM         --normalization_method z-score ^
@REM         --traffic_file %train_data% ^
@REM         --SE_file %SEfile% ^
@REM         --model_file %output_folder_root%/model.pkl ^
@REM         --log_file %output_folder_root%/log.txt ^
@REM         --output_folder %output_folder_root% ^
@REM         --device gpu

@REM set output_folder_root="./output/nor-method-test/log"
@REM python train.py --time_slot 1440 --num_his 5 --num_pred 1 --batch_size 24 ^
@REM         --max_epoch 100 --patience 100 --learning_rate 0.01 ^
@REM         --normalization_method log ^
@REM         --traffic_file %train_data% ^
@REM         --SE_file %SEfile% ^
@REM         --model_file %output_folder_root%/model.pkl ^
@REM         --log_file %output_folder_root%/log.txt ^
@REM         --output_folder %output_folder_root% ^
@REM         --device gpu