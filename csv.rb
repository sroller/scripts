#!/usr/bin/env ruby
#
require 'csv'
# require 'date'
require 'time'
require 'awesome_print'

speed_data = CSV.read('/home/steffenr/data/speedtest.csv', headers: true)
speed_data.each do |r|
	# ap r
	print Time.parse(r['Timestamp']).localtime.strftime("%d-%h-%Y %H:%M"), " "
	printf "Ping: %.0f ms, ", r['Ping']
	printf "Down: %.0f kb/s, ", r['Download'].to_f / (1024*8)
	printf "up  : %.0f kb/s\n", r['Upload'].to_f / (1024*8)
end

