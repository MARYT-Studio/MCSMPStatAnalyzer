import os
import json
import matplotlib.pyplot as plt
import numpy as np
import yaml

# 配置默认值
# 我们关心的数据
INTERESTED_STAT = 'stat.mobKills'
# 是否启用 ID 翻译。若是，还需提供 usernamecache.json
INTERPRET_UUID_AS_PLAYER_ID = True
# 直方图横轴细分区间的个数
DIVISION = 30
# 过滤掉大于这个数值的数据
FILTER_HIGHER_THAN = None


def read_config():
    try:
        cfg_file = open(r'config.yml', 'r', encoding='utf-8')
        config = yaml.safe_load(cfg_file.read())
        global INTERESTED_STAT
        INTERESTED_STAT = config["INTERESTED_STAT"]
        global INTERPRET_UUID_AS_PLAYER_ID
        INTERPRET_UUID_AS_PLAYER_ID = config["INTERPRET_UUID_AS_PLAYER_ID"]
        global DIVISION
        DIVISION = max(config["DIVISION"], 2)
        global FILTER_HIGHER_THAN
        if config["FILTER_HIGHER_THAN"] is not None:
            FILTER_HIGHER_THAN = config["FILTER_HIGHER_THAN"]
        print("读取配置文件成功。")
        return INTERESTED_STAT, INTERPRET_UUID_AS_PLAYER_ID, DIVISION, FILTER_HIGHER_THAN
    except Exception as e:
        print("读取配置文件失败")
        return None


def main(interested_stat, interpret_enabled, division, filter_higher_than):
    with (open(r'output.txt', 'w', encoding='utf-8') as out):
        # 读入文件
        stat_file_list = os.listdir('stats')
        users = {}
        if interpret_enabled:
            try:
                user_names = open(r'usernamecache.json', 'r')
                users = json.load(user_names)
            except Exception as e:
                print("未读取到有效的 usernamecache.json 文件，ID 翻译功能关闭。")
                out.writelines("未读取到有效的 usernamecache.json 文件，ID 翻译功能关闭。\n")
                global INTERPRET_UUID_AS_PLAYER_ID
                INTERPRET_UUID_AS_PLAYER_ID = False

        collect = {}
        # 输出在线玩家总数
        print("本服务器累计在线玩家" + str(len(stat_file_list)) + "人。")
        out.writelines("本服务器累计在线玩家" + str(len(stat_file_list)) + "人。\n")

        # 写收集表
        for stat_file in stat_file_list:
            with open((r'stats/' + stat_file), 'r') as stat:
                stat_dict = json.load(stat)
                uuid = (stat_file.split("."))[0]
                if INTERPRET_UUID_AS_PLAYER_ID:
                    try:
                        collect[users[uuid]] = stat_dict[interested_stat]
                    except KeyError as e:
                        continue
                else:
                    try:
                        collect[uuid] = stat_dict[interested_stat]
                    except KeyError as e:
                        continue

        filtered_keys = []
        for key in collect.keys():
            if collect[key] > filter_higher_than:
                filtered_keys.append(key)

        if len(filtered_keys) > 0:
            print("过滤了满足数值大于等于" + str(filter_higher_than) + "的玩家，共计" + str(len(filtered_keys)) + "人。")
            for key in filtered_keys:
                del collect[key]

        # 输出有效信息比例
        ratio = "%.2f%%" % (100.0 * len(collect) / len(stat_file_list))
        print("其中，统计信息中包含我们所关心的%s数据的人共有%d人，占比%s\n" % (interested_stat, len(collect), ratio))
        out.writelines(
            "其中，统计信息中包含我们所关心的%s数据的人共有%d人，占比%s\n" % (interested_stat, len(collect), ratio))

        # 输出极值
        print("其中，该项统计最大值是%d, 来自玩家%s" % (max(collect.values()), max(collect, key=collect.get)))
        print("而该项统计最小值是%d, 来自玩家%s" % (min(collect.values()), min(collect, key=collect.get)))
        out.writelines([
            "其中，该项统计最大值是%d, 来自玩家%s" % (max(collect.values()), max(collect, key=collect.get)),
            "而该项统计最小值是%d, 来自玩家%s" % (min(collect.values()), min(collect, key=collect.get))
        ])

        # 绘制直方图
        plt.figure(dpi=60, figsize=(30, 20))
        data = list(collect.values())
        n, bins_of_hist, patches = plt.hist(data, bins=division - 1)

        for i in range(len(n)):
            plt.text(float(bins_of_hist[i] + (bins_of_hist[1] - bins_of_hist[0]) / 2), n[i] * 1.01, str(n[i]),
                     ha='center',
                     va='bottom')

        plt.xticks(np.linspace(min(data), max(data), num=division))

        plt.title("Player Stat Distribution Histogram for " + interested_stat)
        plt.xlabel("Stat Value")
        plt.ylabel("Counts")

        plt.show()


result = read_config()
if result is None:
    print("读取配置文件失败，加载默认配置文件")
    with open('config.yml', 'w', encoding='utf-8') as new_cfg:
        new_cfg.writelines([
            '''# 配置选项
# 我们关心的数据
INTERESTED_STAT: 'stat.mobKills'
# 是否启用 ID 翻译。若是，还需提供 usernamecache.json
INTERPRET_UUID_AS_PLAYER_ID: true
# 直方图横轴细分区间的个数
DIVISION: 30
# 过滤掉大于这个数值的数据
FILTER_HIGHER_THAN: 6000'''])
else:
    main(result[0], result[1], result[2], result[3])
