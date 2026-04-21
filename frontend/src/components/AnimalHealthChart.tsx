"use client";

import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useTelemetryStore, TelemetryData } from "@/lib/telemetry";

export default function AnimalHealthChart() {
  const [selectedAnimal, setSelectedAnimal] = useState<string>("");
  const [history, setHistory] = useState<TelemetryData[]>([]);
  const animalPositions = useTelemetryStore((s) => s.animalPositions);
  const telemetryHistory = useTelemetryStore((s) => s.telemetryHistory);

  const animals = Array.from(animalPositions.keys());

  useEffect(() => {
    if (selectedAnimal) {
      const stored = telemetryHistory.get(selectedAnimal);
      if (stored && stored.length > 0) {
        setHistory(stored);
      } else {
        fetch(`/api/telemetry/${selectedAnimal}?hours=24`)
          .then((res) => res.json())
          .then((data) => setHistory(data))
          .catch(console.error);
      }
    }
  }, [selectedAnimal, telemetryHistory]);

  const option = {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
    },
    legend: {
      data: ["Temperature (°C)", "Activity Level"],
      bottom: 0,
    },
    grid: {
      left: "3%",
      right: "3%",
      bottom: "15%",
      top: "10%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: history.map((d) =>
        new Date(d.timestamp * 1000).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })
      ),
      axisLine: { lineStyle: { color: "#86a789" } },
      axisLabel: { color: "#5e7a5e" },
    },
    yAxis: [
      {
        type: "value",
        name: "Temperature (°C)",
        position: "left",
        axisLine: { show: true, lineStyle: { color: "#dc2626" } },
        axisLabel: { formatter: "{value} °C", color: "#dc2626" },
        splitLine: { lineStyle: { color: "#e5e7eb" } },
      },
      {
        type: "value",
        name: "Activity Level",
        position: "right",
        axisLine: { show: true, lineStyle: { color: "#2563eb" } },
        axisLabel: { formatter: "{value}", color: "#2563eb" },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "Temperature (°C)",
        type: "line",
        smooth: true,
        data: history.map((d) => d.temperature?.toFixed(1)),
        itemStyle: { color: "#dc2626" },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(220,38,38,0.3)" },
              { offset: 1, color: "rgba(220,38,38,0.05)" },
            ],
          },
        },
      },
      {
        name: "Activity Level",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        data: history.map((d) => d.activity_level?.toFixed(1)),
        itemStyle: { color: "#2563eb" },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(37,99,235,0.3)" },
              { offset: 1, color: "rgba(37,99,235,0.05)" },
            ],
          },
        },
      },
    ],
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center justify-between">
          <span>Animal Health Metrics</span>
          <Select value={selectedAnimal} onValueChange={(v) => setSelectedAnimal(v || "")}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select animal" />
            </SelectTrigger>
            <SelectContent>
              {animals.length > 0 ? (
                animals.map((id) => (
                  <SelectItem key={id} value={id}>
                    {id}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="none" disabled>
                  No animals online
                </SelectItem>
              )}
            </SelectContent>
          </Select>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {history.length > 0 ? (
          <ReactECharts option={option} style={{ height: "350px" }} />
        ) : (
          <div className="h-[350px] flex items-center justify-center text-muted-foreground">
            {selectedAnimal
              ? "Loading telemetry data..."
              : "Select an animal to view health metrics"}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
