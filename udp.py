no_of_packets = int(input("Enter no of times we received packets: "))
request = {}

for _ in range(no_of_packets):
    t = int(input("provide time in seconds: "))
    packets = int(input("no of packets: "))
    request[t] = packets

max_packet = int(input("provide the maximum packets buffer size:\n"))
rate = int(input("provide the rate at which packets can be sent per second:\n"))

print("input is", request)
print("Max_packets are:", max_packet)
print("Rate per second is:", rate)


def calc_packets(request, max_packet, rate):
    pl = 0                 # packets left in buffer
    packets_dropped = 0
    i = 0
    last_time = max(request.keys())

    while i <= last_time or pl > 0:
        print("------")
        print("Time:", i)
        print("Packets left at start:", pl)

        arrived = request.get(i, 0)
        tl = pl + arrived

        if tl > max_packet:
            dropped = tl - max_packet
            packets_dropped += dropped
            tl = max_packet
            print("Packets dropped:", dropped)

        ps = min(rate, tl)   # packets sent
        tl -= ps
        pl = tl

        print("Packets arrived:", arrived)
        print("Packets sent:", ps)
        print("Packets left at end:", pl)

        i += 1

    return packets_dropped


packets_dropped = calc_packets(request, max_packet, rate)
print("Packets dropped are:", packets_dropped)
