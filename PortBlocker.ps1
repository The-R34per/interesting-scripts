```
function
```
```
 
```
```
Get-ActiveNetworkAdapter
```
```
 {
```
```


```
```
    
```
```
$activeAdapter
```
```
 
```
```
=
```
```
 
```
```
Get-NetAdapter
```
```
 
```
```
|
```
```
 
```
```
Where-Object
```
```
 {
```
```
$_
```
```
.Status
```
```
 
```
```
-eq
```
```
 
```
```
"Up"
```
```
 
```
```
-and
```
```
 
```
```
$_
```
```
.MediaType
```
```
 
```
```
-eq
```
```
 
```
```
"802.3"
```
```
} 
```
```
|
```
```
 
```
```
Select-Object
```
```
 
```
```
-
```
```
First 
```
```
1
```
```


```
```
    
```
```
if
```
```
 (
```
```
$activeAdapter
```
```
) {
```
```


```
```
        
```
```
return
```
```
 
```
```
$activeAdapter
```
```
.Name
```
```


```
```
    } 
```
```
else
```
```
 {
```
```


```
```
        
```
```
$commonNames
```
```
 
```
```
=
```
```
 
```
```
@
```
```
(
```
```
"Ethernet"
```
```
,
```
```
 
```
```
"Local Area Connection"
```
```
,
```
```
 
```
```
"Wi-Fi"
```
```
)
```
```


```
```
        
```
```
foreach
```
```
 (
```
```
$name
```
```
 
```
```
in
```
```
 
```
```
$commonNames
```
```
) {
```
```


```
```
            
```
```
$adapter
```
```
 
```
```
=
```
```
 
```
```
Get-NetAdapter
```
```
 
```
```
-
```
```
Name 
```
```
$name
```
```
 
```
```
-
```
```
ErrorAction SilentlyContinue
```
```


```
```
            
```
```
if
```
```
 (
```
```
$adapter
```
```
 
```
```
-and
```
```
 
```
```
$adapter
```
```
.Status
```
```
 
```
```
-eq
```
```
 
```
```
"Up"
```
```
) {
```
```


```
```
                
```
```
return
```
```
 
```
```
$name
```
```


```
```
            }
```
```


```
```
        }
```
```


```
```
        
```
```
return
```
```
 
```
```
$null
```
```


```
```
    }
```
```


```
```
}
```
```



```
```
function
```
```
 
```
```
Disable-NetworkAdapter
```
```
 {
```
```


```
```
    
```
```
param
```
```
([
```
```
string
```
```
]
```
```
$adapterName
```
```
)
```
```


```
```
    
```
```
if
```
```
 (
```
```
$adapterName
```
```
) {
```
```


```
```
        
```
```
Disable-NetAdapter
```
```
 
```
```
-
```
```
Name 
```
```
$adapterName
```
```
 
```
```
-
```
```
Confirm:
```
```
$false
```
```


```
```
        
```
```
Write-Host
```
```
 
```
```
"Network adapter '
```
```
$adapterName
```
```
' has been disabled."
```
```


```
```
        
```
```
Write-Host
```
```
 
```
```
"All network connections are now blocked."
```
```


```
```
    } 
```
```
else
```
```
 {
```
```


```
```
        
```
```
Write-Host
```
```
 
```
```
"Error: Could not find an active network adapter."
```
```


```
```
        
```
```
exit
```
```
 
```
```
1
```
```


```
```
    }
```
```


```
```
}
```
```



```
```
function
```
```
 
```
```
Enable-NetworkAdapter
```
```
 {
```
```


```
```
    
```
```
param
```
```
([
```
```
string
```
```
]
```
```
$adapterName
```
```
)
```
```


```
```
    
```
```
if
```
```
 (
```
```
$adapterName
```
```
) {
```
```


```
```
        
```
```
Enable-NetAdapter
```
```
 
```
```
-
```
```
Name 
```
```
$adapterName
```
```
 
```
```
-
```
```
Confirm:
```
```
$false
```
```


```
```
        
```
```
Write-Host
```
```
 
```
```
"Network adapter '
```
```
$adapterName
```
```
' has been re-enabled."
```
```


```
```
        
```
```
Write-Host
```
```
 
```
```
"Network connections have been restored."
```
```


```
```
    }
```
```


```
```
}
```
```



```
```
do
```
```
 {
```
```


```
```
    
```
```
$adapterName
```
```
 
```
```
=
```
```
 
```
```
Get-ActiveNetworkAdapter
```
```


```
```
    
```
```


```
```
    
```
```
if
```
```
 (
```
```
-not
```
```
 
```
```
$adapterName
```
```
) {
```
```


```
```
        
```
```
Write-Host
```
```
 
```
```
"No active network adapter found. Please check your network connection."
```
```


```
```
        
```
```
$continue
```
```
 
```
```
=
```
```
 
```
```
Read-Host
```
```
 
```
```
"Do you want to try again? (y/n)"
```
```


```
```
        
```
```
if
```
```
 (
```
```
$continue
```
```
 
```
```
-ne
```
```
 
```
```
"y"
```
```
 
```
```
-and
```
```
 
```
```
$continue
```
```
 
```
```
-ne
```
```
 
```
```
"yes"
```
```
) {
```
```


```
```
            
```
```
break
```
```


```
```
        }
```
```


```
```
        
```
```
continue
```
```


```
```
    }
```
```


```
```
    
```
```


```
```
    
```
```
Write-Host
```
```
 
```
```
"Ready to disable network adapter: '
```
```
$adapterName
```
```
'"
```
```


```
```
    
```
```
$confirm
```
```
 
```
```
=
```
```
 
```
```
Read-Host
```
```
 
```
```
"Do you want to continue? (y/n)"
```
```


```
```
    
```
```


```
```
    
```
```
if
```
```
 (
```
```
$confirm
```
```
 
```
```
-ne
```
```
 
```
```
"y"
```
```
 
```
```
-and
```
```
 
```
```
$confirm
```
```
 
```
```
-ne
```
```
 
```
```
"yes"
```
```
) {
```
```


```
```
        
```
```
break
```
```


```
```
    }
```
```


```
```
    
```
```


```
```
    
```
```
Disable-NetworkAdapter
```
```
 
```
```
-
```
```
adapterName 
```
```
$adapterName
```
```


```
```
    
```
```


```
```
    
```
```
Write-Host
```
```
 
```
```
"Press ENTER to restore network connections..."
```
```


```
```
    
```
```
$null
```
```
 
```
```
=
```
```
 $Host
```
```
.UI.RawUI.ReadKey
```
```
(
```
```
"NoEcho,IncludeKeyDown"
```
```
)
```
```


```
```
    
```
```


```
```
    
```
```
Enable-NetworkAdapter
```
```
 
```
```
-
```
```
adapterName 
```
```
$adapterName
```
```


```
```
    
```
```


```
```
    
```
```
$continue
```
```
 
```
```
=
```
```
 
```
```
Read-Host
```
```
 
```
```
"Do you want to block network connections again? (y/n)"
```
```


```
```
    
```
```


```
```
} 
```
```
while
```
```
 (
```
```
$continue
```
```
 
```
```
-eq
```
```
 
```
```
"y"
```
```
 
```
```
-or
```
```
 
```
```
$continue
```
```
 
```
```
-eq
```
```
 
```
```
"yes"
```
```
)
```
```



```
```
Write-Host
```
```
 
```
```
"Script ended. Network connections are active."
```
```


```
