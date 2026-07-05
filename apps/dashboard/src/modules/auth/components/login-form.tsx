"use client";

import { useFormState } from "react-dom";
import { login } from "../actions/login";
import { Input, Button, Card, CardBody, CardHeader } from "@heroui/react";
import { Mail, Lock } from "lucide-react";

export function LoginForm() {
  const [state, action] = useFormState(login, null);

  return (
    <div className="flex h-screen w-full items-center justify-center bg-background p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="flex flex-col items-start gap-1 pb-2">
          <h1 className="text-xl font-semibold">Sign in to your account</h1>
          <p className="text-sm text-default-500">Enter your details to access the dashboard</p>
        </CardHeader>
        <CardBody>
          <form action={action} className="flex flex-col gap-4">
            <Input
              name="email"
              type="email"
              label="Email"
              placeholder="admin@example.com"
              variant="bordered"
              startContent={<Mail className="text-default-400" size={18} />}
              isRequired
            />
            <Input
              name="password"
              type="password"
              label="Password"
              placeholder="••••••••"
              variant="bordered"
              startContent={<Lock className="text-default-400" size={18} />}
              isRequired
            />
            {state?.error && <p className="text-sm text-danger">{state.error}</p>}
            <Button type="submit" color="primary" className="mt-2">
              Sign In
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
