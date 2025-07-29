wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = '{"sepal_length": 6.765352725982666, "sepal_width": 2.824432849884033, "petal_width": 1.8131520748138428, "petal_length": 4.90852165222168}'

-- Track successful and failed requests
local counter = 0

function response(status, headers, body)
    counter = counter + 1
    if status ~= 200 then
        print("Request " .. counter .. " failed with status: " .. status)
    elseif counter % 100 == 0 then
        print("Completed " .. counter .. " requests")
    end
end

function done(summary, latency, requests)
    print("Total requests: " .. summary.requests)
    print("Total errors: " .. summary.errors.status)
    print("Average latency: " .. latency.mean .. "ms")
    print("Max latency: " .. latency.max .. "ms")
    print("Requests/sec: " .. summary.requests / summary.duration * 1000000)
end
