cpp -nostdinc -I . -undef -x assembler-with-cpp sun5i-brewie.dts sun5i-brewie.preprocessed.dts
dtc -I dts -O dtb -o sun5i-brewie.dtb sun5i-brewie.preprocessed.dts
