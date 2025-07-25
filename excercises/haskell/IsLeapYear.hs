module Main (main) where

main :: IO ()
main = putStrLn (show (isLeapYear 2025))

isLeapYear :: Integer -> Bool
isLeapYear year = year `mod` 400 == 0 || (year `mod` 4 == 0 && year `mod` 100 /= 0)
