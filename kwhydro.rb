#!/usr/bin/env ruby
require 'awesome_print'
require 'time'

# process output from pdftotext

$VERBOSE=true
$VERBOSE=false

SEP="\t"

def extract_data_from_text(text)

    result = { file: text }
    File.open(text, "r") do |f|
        consumption = {off: 0.0, on: 0.0, mid: 0.0}
        days = {days: 0}
        f.each_line do |line|
          # puts "-> #{line}"
            amt = line.match(/(?<consumed>\d+\.\d+)\W+kWh\W+(?<level>Off|Mid|On)\W+Peak/)
            if (amt)
                ap amt if $VERBOSE
                consumption[amt[:level].downcase.to_sym] += amt[:consumed].to_f
            end

            # BILLING DATE and DUE DATE
            b = line.match(/(?<mon>\w{3})\W+(?<day>\d+)\W+(?<year>\d+)\W+(?<mon_due>\w{3})\W+(?<day_due>\d+)\W+(?<year_due>\d+)/)
            if b
                ap b if $VERBOSE
                billing = Date.parse("#{b[:day]}-#{b[:mon]}-#{b[:year]}")
                due_date = Date.parse("#{b[:day_due]}-#{b[:mon_due]}-#{b[:year_due]}")
                result.merge!(billing: billing, due: due_date)
            end

            # Charge period
            # c = line.match(/BILLING DATE\W+DUE DATE\W+Energy\W+Charge\W+(?<from_mon>\w{3})\W+(?<from_day>\d+)\W+(?<from_year>\d{4})\W+to\W+(?<to_mon>\w{3})\W+(?<to_day>\d+)\W+(?<to_year>\d{4})\W*$/)
            # c = line.match(/Energy\W+Charge\W+(?<from_mon>\w{3})\W+(?<from_day>\d+)\W+(?<from_year>\d{4})\W+to\W+(?<to_mon>\w{3})\W+(?<to_day>\d+)\W+(?<to_year>\d{4})\W*$/)
            c = line.match(/\W+(?<from_mon>\w{3})\W+(?<from_day>\d+)\W+(?<from_year>\d{4})\W+to\W+(?<to_mon>\w{3})\W+(?<to_day>\d+)\W+(?<to_year>\d{4})\W*$/)
            if c
                ap c if $VERBOSE
                from_date = Date.parse("#{c[:from_day]}-#{c[:from_mon]}-#{c[:from_year]}")
                to_date =Date.parse("#{c[:to_day]}-#{c[:to_mon]}-#{c[:to_year]}")
                result.merge!(consumption_from: from_date, consumption_to: to_date)
                days[:days] += to_date - from_date
                # STDERR.puts "days: #{days[:days]}"
            end
        end
        result.merge!((consumption).merge(days))
    end
    result
end

def print_header(sep=';')
    puts "due date#{sep}days#{sep}consumption#{sep}daily avg#{sep}on peak#{sep}peak avg#{sep}mid peak#{sep}mid avg#{sep}off peak#{sep}off avg"
end

def print_csv(bill, sep=';')
    sum = bill[:on]+bill[:mid]+bill[:off]
    days = bill[:days].to_i
    avg =  (sum / bill[:days]).to_f

    puts "#{bill[:due].strftime('%Y-%m-%d')}#{sep}#{days}#{sep}#{'%.2f' % sum}#{sep}#{'%.1f' % avg}#{sep}#{'%.2f' % bill[:on]}#{sep}#{'%.2f' % (bill[:on]/days)}#{sep}#{'%.2f' % bill[:mid]}#{sep}#{'%.2f' % (bill[:mid]/days)}#{sep}#{'%.2f' % bill[:off]}#{sep}#{'%.2f' % (bill[:off]/days)}"
end

#
# main
#
text_files = ARGV.empty? ? Dir['**/*.txt'] : ARGV
STDERR.puts "files: #{text_files}" if $VERBOSE

print_header(SEP)

text_files.sort.each do |txt|
  begin
    STDERR.puts "file: #{txt}" if $VERBOSE
    bill = extract_data_from_text(txt)
    ap bill if $VERBOSE
    print_csv(bill, SEP)
  rescue StandardError => e
    # STDERR.puts e.backtrace.inspect.join '\n'
    STDERR.puts "error: #{e} in file: #{txt}"
    exit
  end
end

