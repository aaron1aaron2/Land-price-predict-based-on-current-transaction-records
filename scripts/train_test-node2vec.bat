@REM 關掉回傳命令，不會回傳 bat 程式碼本身
@echo off 

set vars=("walklenghts","numwalks","ps","qs")

set walklengths=(50,80,100)
set numwalks=(50,80,100)
set ps=(0.5,1,2)
set qs=(0.5,1,1.5)

set train_data="./data/train_data/basic/train_data/mean_group0_dist3000.h5"
set SEfile="./data/train_data/basic/SE_data/group0/SE.txt"
set output_folder_root="./output/basic/group0"
python train.py --time_slot 1440 --num_his 5 --num_pred 1 --batch_size 24 ^
        --max_epoch 100 --patience 100 --learning_rate 0.01 ^
        --traffic_file %train_data% ^
        --SE_file %SEfile% ^
        --model_file %output_folder_root%/model.pkl ^
        --log_file %output_folder_root%/log.txt ^
        --output_folder %output_folder_root% ^
        --device gpu

for %%v in %vars% do (
    echo %%v
    if %%v=="numwalks" (
        for %%n in %numwalks% do (
            python data_helper_SE.py --file_path %input_file%^
            --output_folder "data/train_data/SE/test_%%v/D64_WS10_WL80_NW%%n_P2_Q1"^
            --num_walks %%n --id_col new_id --longitude_col lng --latitude_col lat 
        )     
    )

    if %%v=="ps" (
        for %%p in %ps% do (
            python data_helper_SE.py --file_path %input_file%^
            --output_folder "data/train_data/SE/test_%%v/D64_WS10_WL80_NW100_P%%p_Q1"^
            --p %%p --id_col new_id --group_col sarea --longitude_col lng --latitude_col lat 
        )
    )

    if %%v=="qs" (
        for %%q in %qs% do (
            python data_helper_SE.py --file_path %input_file%^
            --output_folder "data/train_data/SE/test_%%v/D64_WS10_WL80_NW100_P2_Q%%q"^
            --q %%q --id_col new_id --group_col sarea --longitude_col lng --latitude_col lat 
        )                        
    )
)

pause