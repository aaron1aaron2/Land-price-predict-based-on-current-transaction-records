@REM 關掉回傳命令，不會回傳 bat 程式碼本身
@echo off 

set vars=("batch_size","learning_rate")

set batch_sizes=(4,8,16,24)
set learning_rates=(0.01,0.001,0.0001)

set train_data="./data/train_data/transaction_amount/train_data/count_group0_dist3000.h5"
set SEfile="./data/train_data/transaction_amount/SE_data/group0/SE.txt"
set output_folder_root="./output/test-hyper-parameter(amount)"

for %%v in %vars% do (
    echo %%v
    if %%v=="batch_size" (
        for %%b in %batch_sizes% do (
            python train.py --time_slot 1440 --num_his 3 --num_pred 1 --batch_size %%b ^
                    --max_epoch 50 --patience 100 --learning_rate 0.001 ^
                    --traffic_file %train_data% ^
                    --SE_file %SEfile% ^
                    --model_file %output_folder_root%/%%v/%%b/model.pkl ^
                    --log_file %output_folder_root%/%%v/%%b/log.txt ^
                    --output_folder %output_folder_root%/%%v/%%b/ ^
                    --device cpu
        )     
    )

    if %%v=="learning_rate" (
        for %%l in %learning_rates% do (
            python train.py --time_slot 1440 --num_his 3 --num_pred 1 --batch_size 16 ^
                    --max_epoch 50 --patience 100 --learning_rate %%l ^
                    --traffic_file %train_data% ^
                    --SE_file %SEfile% ^
                    --model_file %output_folder_root%/%%v/%%l/model.pkl ^
                    --log_file %output_folder_root%/%%v/%%l/log.txt ^
                    --output_folder %output_folder_root%/%%v/%%l ^
                    --device cpu
        )
    )
)

pause