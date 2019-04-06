# Distributed Group Membership

Python实现，基于Gossip协议。



## Usage

### Configuration

在 `conf.yaml` 中配置introducer ip、端口和一些时间阈值。



### Operation

- 加入：运行后该节点会自动加入group；

  ```
  python server.py
  ```

- 离开：输入 `leave`；
- 查看成员列表：输入 `list`；

- 查看本节点信息：输入 `self`；

- 失败：关机断网砸电脑等。



## Design

### Algorithm

把 01 节点作为introducer。认为节点们组成了一个环，每个节点会定期随机选择一个节点向其发送rumor，格式如下：

<table>
	<tr>
		<td>heartbeat id（每heartbeat一次id都会+1）</td>
		<td>timestamp（heartbeat时间戳）</td>
		<td>status（节点状态）</td>
	</tr>
</table>


节点将根据 `conf.yaml` 中的配置定期刷新成员列表，并将超过一定时间没收到rumor的节点置于 `SUSPECTED` 状态或判定它失败。

**Join：** 若一个节点想要加入 group，它会向 introducer 发送 `JOINED` 消息。如果 introducer 已经加入了 group，其他节点将更新自己维护的成员列表等信息； 如果 introducer 不在 group 内，则没有新节点可以加入该 group，但 group 中的节点可以继续正常运作。其他节点会 heartbeat 一次并向它发送 rumor，包含已经加入或离开的节点的信息。

**Leave：** 若一个节点想要离开 group，它会向成员列表中的其他节点发送 `LEFT` 消息，并停止向其其他节点发送 rumor。

**Crash：** 一个节点失败后，它将不会向它的邻居节点发送rumor。超过一定时间（在 `conf.yaml` 中配置）没有节点收到它的rumor后，它将被置为"可疑"状态；再过一定时间没有节点收到它的rumor后，它将被判为已失败。它可以向 introducer 发送新的 `JOINED` 请求并重新加入 group。



### Scalability

不管 N 是多少，每个节点都会定期向其他节点发送rumor，每个节点负载几乎相同，所以该算法可以扩展到 N 个节点。



### Assignment 2 (Distributed Log Query Processing System)

Assignment 2 可以在客户端使用 grep 查询集群中所有机器上的日志，而无需重复登录每个机器并多次输入命令，为测试提供了很大的便利。



## Test

### False Positive Rate

丢失消息实现方法：假设丢失率为 m%，随机一个 0-99 之间的整数，若该数 < m 则不发送rumor。

1. N = 2 的误报率高于 N = 4。因为如果在 N=4 的集群有一个节点的消息丢失，其他节点可能依然能从之前收到过该节点的消息的节点处获得正确的成员列表。而在 N=2 的集群中，一个节点的消息丢失后，就没有多余的节点有正确成员列表的备份，所以误报率更高。
2. 误报率随消息丢失率增加而增加。一个节点丢失的消息越多，其他节点越有可能收不到它的heartbeats而把它判为失败节点。
3. 消息丢失率较小（3％和10％）时，误报率较小；消息丢失率较高时（30％），误报率迅速增加。所以只要损失率在可接受的范围内，该分布式系统就可以较稳定的运作。