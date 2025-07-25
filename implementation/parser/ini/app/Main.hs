module Main (main) where

import Lib

main :: IO ()
main = do
    let iniLines =
            [ "; This is a comment"
            , "[Section1]"
            , "key1=value1"
            , "key2=value2"
            , ""
            , "[Section2]"
            , "keyA=valueA"
            ]

    let parsedData = parseIniLines iniLines
    print parsedData
