# Valorant Shop Checker

### Local script to check multiple accounts shops and stuff
### Most of the code (riot auth) came from https://github.com/GamerNoTitle/Valora so shout out that guy

### Usage: 
- Modify/create a file in the same directory as `main.py` called `config.yaml` and make it look something like:

```text
accounts:
  - user: test
    pw: pass
  - user: account2
    pw: pass3
```

- Run the following:

```shell
python ./main.py
```

- To open all images automatically in browser:
```shell
python ./main.py --open-images
```

- To pass a separate config file:
```shell
python ./main.py -c config2.yaml
```

- To pass specific accounts to check:
```shell
python ./main.py --accounts profile1,profile3
```

- Exit instead of printing and waiting for user input
```shell
python ./main.py --dont-stall
```

- You can combine different parameters:
```shell
python ./main.py -c config2.yaml --open-images --dont-stall
```
