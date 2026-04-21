"use client";

import { useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useTelemetryStore, AlertData } from "@/lib/telemetry";

export default function AlertTable() {
  const alerts = useTelemetryStore((s) => s.alerts);

  useEffect(() => {
    fetch("/api/alerts")
      .then((res) => res.json())
      .then((data) => {
        data.forEach((alert: AlertData) => {
          useTelemetryStore.getState().addAlert(alert);
        });
      })
      .catch(console.error);
  }, []);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center justify-between">
          <span>Recent Alerts</span>
          <Badge variant="destructive" className="bg-red-100 text-red-700 border-red-200">
            {alerts.length} Events
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {alerts.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow className="bg-green-50 hover:bg-green-100">
                <TableHead className="text-green-900">Timestamp</TableHead>
                <TableHead className="text-green-900">Animal ID</TableHead>
                <TableHead className="text-green-900">Alert Type</TableHead>
                <TableHead className="text-green-900">Location</TableHead>
                <TableHead className="text-green-900">Expected Paddock</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {alerts.map((alert) => (
                <TableRow key={alert.id}>
                  <TableCell className="font-mono text-sm">
                    {new Date(alert.timestamp * 1000).toLocaleString()}
                  </TableCell>
                  <TableCell className="font-medium">
                    <Badge variant="outline" className="border-green-600 text-green-700">
                      {alert.belt_id}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="destructive">Geofence Breach</Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {alert.latitude.toFixed(4)}, {alert.longitude.toFixed(4)}
                  </TableCell>
                  <TableCell className="text-sm">{alert.paddock_id}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            No alerts - All animals within geofences
          </div>
        )}
      </CardContent>
    </Card>
  );
}
