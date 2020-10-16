# Script to run clang formatting on all code contained
find -iname *.h -o -iname *.cpp | xargs -d '\n' clang-format -i