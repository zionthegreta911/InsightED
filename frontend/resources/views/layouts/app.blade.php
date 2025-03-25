<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Student Analysis</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}"> <!-- Adjust if needed -->
</head>
<body>

    <nav>
        <h2>AI-Powered Student Analysis</h2>
    </nav>

    <div class="container">
        @yield('content')  <!-- This is where child views will be inserted -->
    </div>

    <script src="{{ asset('js/dashboard.js') }}"></script>
</body>
</html>
